# S12 — Estrategia de datos, caché y consistencia

## 1. Qué se entregó

- Tabla **operación → garantía** con las operaciones reales del sistema:
  [`../datos/consistencia.md`](../datos/consistencia.md).
- Caché de lectura con TTL, invalidación por escritura y contadores observables (ADR 0013).
- Id reservado de forma atómica con `DocumentReference.create()` (ADR 0011).
- Evento `documento.publicado` con deduplicación y DLQ (ADR 0015).
- C4 nivel 2 con **Firestore como contenedor de datos externo** (`ContainerDb_Ext`), caché y outbox
  como contenedores propios y la aclaración de que **no hay broker**: el outbox es memoria del
  proceso ([`../c4/nivel-2.md`](../c4/nivel-2.md)).
- Pruebas: `tests/test_cache.py`, `tests/test_idempotencia.py`.

## 2. Garantías por operación (resumen)

| Operación | Garantía | Qué la sostiene |
|---|---|---|
| Publicar | Fuerte para unicidad de id; exactamente una vez por `Idempotency-Key` | `create()` + `AlreadyExists`; clave + hash |
| Buscar | Eventual entre instancias acotada por TTL; *read-your-writes* en la instancia que publica | Caché + invalidación en `crear_documento` |
| Consumir evento | Al menos una vez; efecto una vez | `ProcesadorIdempotente` + comprobación por `id_documento` |
| Resolver revisión | Fuerte dentro de la instancia | Lock + retiro de la cola |
| Métrica | Efímera | Contadores en memoria (ADR 0008) |

## 3. La caché en concreto

| Pregunta | Respuesta |
|---|---|
| Qué se cachea | Lista completa de documentos públicos (sin campos internos), ordenada por id |
| Dónde | Memoria del proceso (`_CacheDocumentos`) |
| TTL | 60 s por defecto (`SHAREU_CACHE_TTL_SEGUNDOS`); `0` la apaga |
| Invalidación | Toda escritura llama a `_cache.invalidar()` antes de responder |
| Observabilidad | `GET /documentos/cache` y `GET /administracion/cache` |
| Lo que no hace | No hay *single-flight*: la caché fría concurrente genera lecturas extra |

### Por qué invalidar y no solo TTL

Con solo TTL, un estudiante publicaría y no vería su documento hasta 60 s después. Ese es el fallo
que la ficha pide resolver. La prueba `test_la_publicacion_queda_visible_en_la_busqueda` llena la
caché, publica y verifica que la siguiente búsqueda ya ve el documento. `test_una_escritura_invalida_la_cache`
verifica el contador de invalidaciones. El TTL queda como red de seguridad para cambios hechos por
fuera del proceso (consola de Firebase u otra instancia).

### Costo medido

| Configuración | Lecturas / búsqueda | Fuente |
|---|---:|---|
| Sin caché | 1,00 | `mediciones/s10-linea-base-sin-cache.json` |
| Con caché | 0,07 | `mediciones/s14-local-asgi.json` |

La diferencia entre 0,07 y 0 se explica por el *stampede* de la primera repetición y por la
invalidación deliberada entre repeticiones del banco de pruebas.

## 4. La decisión de datos más costosa de revertir

No es el motor ni la caché: es el **tipo e identidad de los ids** (ADR 0011). El entero sale del
almacén, se copia al contrato (`id: integer`), al frontend (`Documento.id: number`) y a futuras
referencias (`documento_id`). Cambiarlo después de tener datos exige migrar documentos y
referencias, publicar una versión mayor y romper clientes. Firestore está confinado a
`repository.py`; la caché es derivada y se reconstruye.

## 5. Pruebas y verificación

```bash
pytest tests/test_cache.py tests/test_idempotencia.py -q
```

Se rompió a propósito la invalidación (se comentó `_cache.invalidar()`) y la prueba de visibilidad
falló; se restauró. Se rompió la deduplicación del consumidor y
`test_un_duplicado_no_crea_dos_entradas_de_revision` falló; se restauró. Esa es la evidencia de que
las pruebas cubren el defecto y no solo acompañan al código.

## 6. Trazabilidad

`docs/aspectos.md` (A2, A4, A8) → ADR 0011, 0013 → `app/documentos/repository.py` →
`tests/test_cache.py` → [`../datos/consistencia.md`](../datos/consistencia.md) → este documento →
`docs/evidencia/s12-taller-mensajes.md`.
