# Estrategia de datos: consistencia, caché y eventos

Evidencia S12. El sistema real es un backend FastAPI (una instancia) con Firestore como almacén
externo, una caché de lectura en proceso y un outbox en proceso para el evento
`documento.publicado`. Las operaciones de la tabla son las que existen en el código, no ejemplos
genéricos.

## 1. Tabla operación → garantía

| Operación real | Ruta / código | Garantía declarada | Qué la sostiene | Qué se acepta |
|---|---|---|---|---|
| **Publicar documento** (crear metadatos) | `POST /documentos` → `documentos.repository.crear_documento` | **Fuerte para la unicidad del id**; **exactamente una vez por `Idempotency-Key`** mientras el proceso viva | `DocumentReference.create()` + `AlreadyExists` (`_reservar_id_y_crear`); búsqueda por `idempotency_key` + hash del cuerpo antes de crear; 409 si el cuerpo cambia | Si el proceso se reinicia entre el `create` y la respuesta, el cliente debe reintentar con la misma clave; el documento ya existe y se devuelve con 200 |
| **Leer / buscar documentos** | `GET /busqueda/documentos` → `documentos.repository.listar_documentos` | **Eventual** entre instancias, acotada por el TTL; **read-your-writes** en la instancia que publicó | Caché en memoria; `_cache.invalidar()` al final de `crear_documento`; TTL por defecto 60 s | Otra instancia (si existiera) puede tardar hasta el TTL en ver el documento; hoy hay una sola instancia |
| **Consumir `documento.publicado`** | `app/eventos/outbox.py` → `administracion.revision.registrar_para_revision` | **Al menos una vez**; efecto **exactamente una vez** por deduplicación | `ProcesadorIdempotente` por `event_id` + comprobación por `id_documento` en la bandeja | Un evento puede entregarse dos veces; se descarta. Un reinicio pierde eventos pendientes (límite del outbox) |
| **Resolver revisión** | `POST /administracion/revision/{id}/resolver` | **Fuerte dentro de la instancia** (lectura y borrado bajo el mismo lock) | `threading.Lock` en `revision.py`; la entrada se retira de la cola y se devuelve con estado `aprobado` | No hay persistencia: un reinicio vacía la bandeja |
| **Registrar métrica de búsqueda** | `administracion.metricas.registrar_busqueda` | **Eventual / efímera** | Contadores en memoria | Se pierden al reiniciar; es una métrica operativa, no un registro contable (ADR 0008) |
| **Cargar datos de ejemplo** | `documentos.repository._inicializar` | **Idempotente** | `limit(1).stream()` antes del batch; solo si la colección está vacía | Dos procesos arrancando a la vez podrían intentar sembrar; el `create`/id fijo lo hace converger, pero no se diseñó para multinstancia |

## 2. Dos operaciones contrastadas con el código

### 2.1 Publicar: la unicidad la garantiza Firestore, no el código

`_reservar_id_y_crear` (`app/documentos/repository.py`) calcula `primer_id = max(id) + 1` y llama a
`referencia.create(documento)`. Si otro escritor ya tomó ese id, Firestore responde
`AlreadyExists`, el bucle prueba el siguiente candidato (hasta 5) y solo entonces falla con
`ErrorPersistencia`.

```python
for candidato in range(primer_id, primer_id + intentos):
    nuevo = {"id": candidato, **datos}
    referencia = coleccion.document(str(candidato))
    try:
        _con_reintentos(lambda: referencia.create(nuevo))
    except AlreadyExists:
        continue
    return nuevo
```

Esto es lo que hace **fuerte** la garantía de unicidad: no se usa `set()` (sobrescribiría) ni un
`SELECT MAX + 1` confiado en la ausencia de concurrencia. Pruebas:
`test_reservar_id_salta_un_id_que_otro_escritor_tomo` y `test_dos_publicaciones_no_repiten_id`.

La idempotencia de la **operación completa** se apoya en `idempotency_key`: antes de crear se
busca una coincidencia (`_buscar_por_idempotencia`); si existe y el hash SHA-256 del cuerpo coincide,
se devuelve el documento con `creado=False`; si el hash difiere, se lanza `ConflictoIdempotencia`
(HTTP 409). La ventana entre la búsqueda y el `create` no es atómica, pero dos solicitudes
concurrentes con la misma clave y el mismo cuerpo acaban con un documento y un `AlreadyExists` como
mucho; el cliente reintenta y recibe 200. Es el compromiso declarado para no introducir una
transacción distribuida.

### 2.2 Buscar: la escritura invalida la caché; el TTL cubre lo externo

`crear_documento` termina con `_cache.invalidar()` **antes** de devolver el documento. La
siguiente llamada a `listar_documentos(usar_cache=True)` encuentra la caché vacía, lee Firestore y
guarda la lista nueva. La prueba `test_la_publicacion_queda_visible_en_la_busqueda` publica y
verifica que la búsqueda inmediata lo ve.

El TTL no es la política principal: es la red de seguridad para cambios hechos **por fuera** del
proceso (consola de Firebase u otra instancia). Si solo existiera TTL, el usuario publicaría y
podría no ver su documento hasta 60 s después; ese es exactamente el fallo que la ficha S12 pide
resolver.

## 3. Diseño de caché

| Pregunta | Respuesta |
|---|---|
| **Qué se cachea** | La lista completa de documentos **públicos** (sin `idempotency_key`, `idempotency_hash` ni `creado_en`), ordenada por id |
| **Dónde** | Memoria del proceso del backend (`_CacheDocumentos`), una entrada por instancia |
| **Cuánto tiempo** | TTL de 60 s por defecto (`SHAREU_CACHE_TTL_SEGUNDOS`); `0` la apaga |
| **Qué la invalida** | Toda escritura de `documentos` (`_cache.invalidar()` en `crear_documento` y `invalidar_cache()`); también el vencimiento del TTL |
| **Cómo se observa** | `GET /documentos/cache` y `GET /administracion/cache`: `ttl_segundos`, `entradas`, `hits`, `misses`, `invalidaciones`, `expira_en_segundos` |
| **Qué no hace** | No hay *single-flight*: N solicitudes concurrentes con la caché fría pueden leer Firestore N veces. Medido y aceptado (S14: 21 lecturas en 300 búsquedas) |
| **Cómo se prueba** | `tests/test_cache.py` (segunda lectura no va a Firestore, TTL expira, escritura invalida, no se muta desde fuera) |

## 4. Garantías del flujo por eventos

- **Garantía elegida: al menos una vez.** El productor publica en el outbox y el despacho ocurre en
  `BackgroundTasks`, después de responder. Un fallo del consumidor no se propaga al productor.
- **Lo que se asume:** el mismo `event_id` puede llegar más de una vez; el consumidor
  (`ProcesadorIdempotente`) descarta duplicados y la bandeja además comprueba `id_documento`. Un
  reinicio descarta eventos pendientes y la DLQ, porque el outbox es en memoria.
- **Reintentos:** 3 intentos con espera 1 s y 2 s; luego `fallidos` (DLQ en memoria) con
  `ultimo_error` e `intentos`.
- **Contrato:** `docs/eventos/contrato-evento.md` y `documento-publicado.schema.json`, versión 1.
  Cambio compatible: agregar un campo opcional al payload. Incompatible: quitar/renombrar un campo,
  cambiar su tipo o el significado; exige subir `version` y un consumidor nuevo.
- **Trazabilidad:** `event_id` y `correlation_id` (el `request_id` HTTP) en cada línea de log;
  contadores en `GET /administracion/eventos`.

## 5. La decisión de datos más costosa de revertir

Es el **tipo e identidad de los ids** ([ADR 0011](../adr/0011-identidad-de-datos-y-propiedad-por-modulo.md)),
no el motor ni la caché. El id entero sale del almacén, se copia en el contrato (`id: integer`), en
el frontend (`Documento.id: number`) y en las referencias futuras (`documento_id`). Cambiarlo a UUID
después de tener datos reales exige migrar documentos y referencias, publicar una versión mayor del
contrato y romper clientes. El motor Firestore, en cambio, está confinado a
`app/documentos/repository.py`; la caché es derivada y se reconstruye.

## 6. Lo que no cubre este diseño

- No hay transacciones entre Firestore y la bandeja de revisión: se usa un outbox, no una saga,
  porque el segundo efecto es recuperable y no requiere compensación.
- No hay consistencia fuerte entre instancias; el despliegue actual tiene una sola.
- No hay persistencia del outbox; un reinicio puede perder un aviso de revisión. El documento
  publicado sigue existiendo y la bandeja puede reconstruirse manualmente desde Firestore.
