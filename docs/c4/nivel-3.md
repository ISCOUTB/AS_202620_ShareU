# C4 — Nivel 3: componentes del contenedor API

Diagrama editable: [`nivel3.mmd`](nivel3.mmd). Niveles anteriores: [`nivel1.mmd`](nivel1.mmd) y
[`nivel-2.md`](nivel-2.md). Este nivel descompone **solo** el contenedor `api`; la aplicación web
y Firestore se mantienen como contextos externos para no duplicar el nivel 2.

## Componentes y responsabilidad

| Componente | Responsabilidad | Código | Depende de |
|---|---|---|---|
| Middlewares HTTP | Asigna `request_id`, escribe una línea JSON por solicitud, aplica CORS y cabeceras | `app/main.py` | — |
| Seguridad | `exigir_token_admin`: 503 si falta configuración, 401 si el token no coincide, comparación en tiempo constante | `app/seguridad/autenticacion.py` | Configuración |
| Router usuarios | Verificación del módulo; el registro de cuentas sigue fuera de alcance | `app/usuarios/router.py` | — |
| Router documentos | Valida el cuerpo, exige token e `Idempotency-Key`, publica el evento después de responder | `app/documentos/router.py` | Servicio documentos, seguridad, outbox |
| Router búsqueda | Traduce los filtros HTTP y devuelve `total` + `resultados`; convierte el fallo de persistencia en 503 | `app/busqueda/router.py` | Servicio búsqueda |
| Router calificaciones | Verificación del módulo; las valoraciones por usuario siguen fuera de alcance | `app/calificaciones/router.py` | — |
| Router administración | Métricas, eventos, caché y bandeja de revisión; las rutas con datos de autores exigen token | `app/administracion/router.py` | Servicio administración, seguridad |
| Servicio documentos | Interfaz pública del dominio: `obtener_documentos`, `registrar_documento`, estadísticas de caché | `app/documentos/service.py` | Repositorio documentos |
| Repositorio documentos | Lee y crea en Firestore; reserva id con `create()`; reintentos y timeout; hash de idempotencia | `app/documentos/repository.py` | Firestore, caché |
| Caché de lectura | Lista pública con TTL de 60 s, hits/misses e invalidación tras escritura | `app/documentos/repository.py` (`_CacheDocumentos`) | Memoria del proceso |
| Servicio búsqueda | Combina los filtros, ordena por calificación y título, recorta campos internos y registra la métrica | `app/busqueda/service.py` | Servicio documentos, servicio administración |
| Servicio administración | Fachada del módulo; evita que búsqueda importe `metricas.py` o `revision.py` (ADR 0008) | `app/administracion/service.py` | Métricas, revisión, eventos, caché de documentos |
| Métricas de búsqueda | Contadores de búsquedas y de búsquedas sin resultados | `app/administracion/metricas.py` | Memoria del proceso |
| Bandeja de revisión | Consumidor idempotente de `documento.publicado`; lista y resuelve entradas | `app/administracion/revision.py` | Outbox (tipos y `ProcesadorIdempotente`) |
| Outbox en proceso | Publica, despacha, reintenta (1 s y 2 s), deduplica por `event_id` y acumula fallidos | `app/eventos/outbox.py` | Memoria del proceso |

## Flujo de búsqueda (camino principal)

```text
GET /busqueda/documentos?materia=Programación
  -> Router búsqueda
  -> Servicio búsqueda
  -> Servicio documentos -> Repositorio documentos
       -> Caché (hit)  : devuelve la lista sin tocar Firestore
       -> Caché (miss) : Firestore -> _publico() -> Caché
  -> filtros + orden + métrica
  -> 200 {"total": n, "resultados": [...]}
```

El servicio de búsqueda copia cada documento antes de recortar `palabras_clave`, porque la lista
la comparte la caché. La caché se invalida al crear un documento para que el autor vea su propia
publicación sin esperar el TTL.

## Flujo de publicación y evento

```text
POST /documentos  (X-Admin-Token, Idempotency-Key, JSON)
  -> Router documentos -> Seguridad (401/503)
  -> Servicio documentos -> Repositorio documentos
       -> buscar clave de idempotencia + hash SHA-256
       -> Firestore create() con el primer id libre
       -> invalidar caché
  -> 201 (creado) / 200 (reintento) / 409 (cuerpo distinto) / 503 (Firestore)
  -> outbox.publicar("documento.publicado")
  -> BackgroundTasks.despachar()  (después de responder)
       -> Bandeja de revisión (deduplicación por event_id y por id_documento)
```

## Caminos de error del componente

| Situación | Componente que decide | Respuesta |
|---|---|---|
| Falta `SHAREU_ADMIN_TOKEN` | Seguridad | 503 fail-closed |
| Token incorrecto | Seguridad | 401 |
| Cuerpo inválido o `min_calificacion` fuera de [0, 5] | FastAPI/Pydantic | 422 |
| Firestore no responde o responde tarde | Repositorio → Router | 503 con detalle genérico |
| Misma clave de idempotencia con otro cuerpo | Repositorio → Router | 409 |
| Consumidor del evento falla | Outbox | Reintenta y, tras 3 intentos, DLQ |
| Evento duplicado | Bandeja de revisión | Se descarta; no crea otra entrada |

## Fronteras y trazabilidad

- **Regla:** un módulo solo importa la interfaz `service.py` de otro. `tests/test_fronteras.py`
  inspecciona los imports y falla si aparece un cruce prohibido.
- **Dependencias permitidas:** búsqueda → documentos y administración; administración → documentos
  (solo estadísticas de caché); documentos → eventos y seguridad; administración.revision → eventos.
- **Estilo:** [ADR 0001](../adr/0001-estilo-arquitectonico.md).
- **Persistencia:** [ADR 0012](../adr/0012-persistencia-en-firestore.md).
- **Caché:** [ADR 0013](../adr/0013-cache-de-lectura-con-invalidacion.md).
- **Seguridad:** [ADR 0014](../adr/0014-endurecimiento-http-y-escritura-autenticada.md).
- **Mensajería:** [ADR 0015](../adr/0015-mensajeria-asincrona-con-outbox.md).
- **Métrica:** [ADR 0008](../adr/0008-metrica-tras-interfaz-de-administracion.md) y
  [ADR 0016](../adr/0016-medicion-de-latencia-y-costo-de-lecturas.md).
- **Aspectos:** [`../aspectos.md`](../aspectos.md), filas A1–A10.

## Qué no aparece en este nivel

No hay broker, cola persistente, caché distribuida, servicio de archivos ni componente generativo.
El outbox y la caché son estructuras en memoria del proceso; dibujarlos como contenedores externos
sería afirmar una infraestructura que el sistema no tiene.
