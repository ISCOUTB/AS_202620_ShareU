# 6. Vista de ejecución

## 6.1 Escenario A: buscar material (síncrono, camino crítico)

Contrato: [`docs/api/openapi.yaml`](../api/openapi.yaml), `GET /busqueda/documentos`. El estudiante
espera la respuesta para ver los resultados; por eso el borde es síncrono (ADR 0004).

| Paso | De → a | Protocolo / formato | Naturaleza |
|---|---|---|---|
| 1 | Estudiante → aplicación web | HTTPS | Síncrona |
| 2 | Aplicación web → `busqueda.router` | `GET /busqueda/documentos?...` JSON/HTTPS; timeout 15 s, 1 reintento | Síncrona |
| 3 | `busqueda.router` → `busqueda.service` | Función Python | In-process |
| 4 | `busqueda.service` → `documentos.service` | Función Python (interfaz de servicio) | In-process |
| 5a | `documentos.service` → caché | Lectura de memoria si el TTL no venció | In-process |
| 5b | `documentos.service` → `documentos.repository` → Firestore | `firebase-admin`, gRPC/HTTPS; timeout 2 s, 3 intentos | Síncrona (solo en *miss*) |
| 6 | `busqueda.service` → `administracion.service` | Función Python: registra la métrica | In-process |
| 7 | Respuesta al navegador | JSON validado contra `ResultadoBusqueda` | Síncrona |

```text
Estudiante
   | HTTPS
   v
Web (Next.js) --GET /busqueda/documentos, JSON/HTTPS--> busqueda.router
                                                          | función
                                                          v
                                                    busqueda.service
                                                       |        |
                                     función (interfaz)        | métrica
                                                       v        v
                                              documentos.service  administracion.service
                                                 |        |
                                        caché (hit)       | (miss)
                                                 |        v
                                                 |   repository --gRPC/HTTPS--> Firestore
                                                 v
                                             respuesta JSON
```

**Caché fría concurrente:** si N solicitudes llegan con la caché vacía, cada una puede leer
Firestore (no hay *single-flight*). Es una limitación conocida, medida en S14 (21 lecturas en 300
búsquedas) y declarada en §11.

## 6.2 Escenario B: publicar un documento (síncrono + efecto asíncrono)

| Paso | De → a | Protocolo / formato | Naturaleza |
|---|---|---|---|
| 1 | Administrador → web → API | `POST /documentos`, JSON/HTTPS, `X-Admin-Token`, `Idempotency-Key` | Síncrona |
| 2 | `documentos.router` → `seguridad` | Verificación del token (comparación en tiempo constante) | In-process |
| 3 | `documentos.router` → `documentos.service` | Función Python | In-process |
| 4 | `documentos.service` → `repository` | Búsqueda por `idempotency_key` + hash del cuerpo | In-process |
| 5 | `repository` → Firestore | `DocumentReference.create()`, timeout 2 s, 3 intentos | Síncrona |
| 6 | `repository` invalida la caché | `_cache.invalidar()` antes de devolver | In-process |
| 7 | `documentos.router` → outbox | `eventos.publicar("documento.publicado", …)`; el `correlation_id` es el `request_id` | In-process |
| 8 | API → administrador | **201** si creó, **200** si fue un reintento idempotente, **409** si la clave cambió de cuerpo, **503** si Firestore falla | Síncrona |
| 9 | `BackgroundTasks` → `despachar` | Después de la respuesta; el consumidor actualiza la bandeja | Asíncrona |

```text
Administrador
   | POST /documentos + token + Idempotency-Key
   v
router --token--> seguridad
   |
   v
service --clave+hash--> repository --create()--> Firestore
   |                        |
   |                        +--> invalidar caché
   +--> publicar evento --> outbox (memoria)
   |
   +--> 201/200/409/503 (respuesta)
                              |
                     BackgroundTasks: despachar
                              |
                              v
                    administracion.revision (dedup por event_id)
```

**Si el consumidor falla**, el outbox reintenta 1 s y 2 s; al tercer fallo el evento pasa a la
DLQ en memoria. La publicación **no** se cae: el documento ya está persistido y la respuesta ya
salió. Si el administrador reintenta la misma publicación, la clave de idempotencia devuelve 200 y
**no** se emite un segundo evento.

## 6.3 Escenario C: Firestore no responde o responde tarde

1. `_con_reintentos` agota 3 intentos con timeout de 2 s.
2. Se lanza `ErrorPersistencia`.
3. El router traduce a **503** con un mensaje genérico; no se filtra la traza al cliente.
4. El middleware registra la solicitud con `status_code=503` y `duration_ms`.
5. `/health` sigue respondiendo `{"estado":"ok"}`: el proceso está vivo y el fallo es de la
   dependencia, no del contenedor.
6. Para una búsqueda, la caché puede servir una lista previa si el TTL no venció; si no, el
   estudiante ve el mensaje de error del frontend y puede reintentar.

## 6.4 Escenario D: sin resultados

La API devuelve **200** con `total: 0` y lista vacía (ejemplo `sinResultados` del contrato). No es
un error: el frontend muestra «Nada por aquí. Prueba otra palabra clave». La métrica
`tasa_busquedas_sin_resultados` se incrementa y es la señal de usabilidad que vigila el equipo.

## 6.5 Resumen de naturaleza por integración

| Integración | Naturaleza | Formato | Por qué |
|---|---|---|---|
| Navegador → web | Síncrona | HTTPS | El estudiante ve la página |
| web → API | Síncrona | JSON/HTTPS | Necesita el resultado en la misma interacción |
| `busqueda` → `documentos` | Síncrona, in-process | Función Python | Ya lo fija el monolito modular (ADR 0001) |
| API → Firestore | Síncrona | gRPC/HTTPS | La respuesta depende del dato |
| documentos → outbox → administración | Asíncrona | Evento en proceso | Efecto secundario; no debe acoplar la disponibilidad (ADR 0015) |
| API → administrador | Síncrona | `X-Admin-Token` | Autorización del MVP (ADR 0014) |
