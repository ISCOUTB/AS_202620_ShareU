# 5. Vista de bloques de construcción

## 5.1 Sistema completo

```text
app.main
  |
  +--> usuarios.router        (ping; registro pendiente)
  +--> documentos.router ----> documentos.service ----> documentos.repository ----> Firestore
  |        |                          |
  |        |                          +--> _CacheDocumentos (TTL + invalidación)
  |        +--> eventos.publicar ----> outbox en proceso ----> administracion.revision
  |
  +--> busqueda.router ------> busqueda.service ------> documentos.service
  |                                            +-----> administracion.service (métrica)
  +--> calificaciones.router  (ping; valoraciones pendientes)
  +--> administracion.router -> administracion.service -> metricas / revision / eventos / caché
  +--> seguridad.exigir_token_admin (dependencia de las rutas protegidas)
```

`app/main.py` es el punto de composición: monta routers, registra la suscripción al evento, agrega
middlewares y configura el logging. No contiene lógica de dominio.

## 5.2 Responsabilidades

| Bloque | Responsabilidad | Ubicación | Depende de |
|---|---|---|---|
| Usuarios | Cuentas y autenticación (futuro) | `app/usuarios/` | — |
| Documentos | Metadatos, persistencia, idempotencia, caché | `app/documentos/` | Firestore, `eventos` |
| Búsqueda | Filtros, palabra clave y orden | `app/busqueda/` | `documentos.service`, `administracion.service` |
| Calificaciones | Valoraciones por usuario (futuro) | `app/calificaciones/` | — |
| Administración | Métricas, eventos, bandeja de revisión y resolución | `app/administracion/` | `eventos` (solo lectura del contrato) |
| Eventos | Outbox, suscripción, reintentos, DLQ, deduplicación | `app/eventos/` | — |
| Seguridad | Verificación de la credencial administrativa | `app/seguridad/` | Configuración |

## 5.3 Regla de dependencias

Un módulo solo puede importar la **interfaz de servicio** de otro (`app/<modulo>/service.py`), nunca
su `repository.py`, `router.py` ni archivos internos. Las dependencias permitidas hoy son:

- `busqueda.service` → `documentos.service` (lectura de documentos).
- `busqueda.service` → `administracion.service` (registro de la métrica, ADR 0008).
- `documentos.router` → `eventos` (publicar) y `seguridad` (token).
- `administracion.revision` → `eventos` (tipos `Evento` y `ProcesadorIdempotente`), sin importar
  `documentos`.

`tests/test_fronteras.py` inspecciona los imports y falla si aparece un cruce prohibido.

## 5.4 Bloques internos relevantes

| Bloque | Qué hace | Dónde |
|---|---|---|
| `_reservar_id_y_crear` | Reserva id con `create()` atómico y prueba el siguiente ante `AlreadyExists` | `app/documentos/repository.py` |
| `_buscar_por_idempotencia` | Busca la clave y compara el hash SHA-256 del cuerpo | `app/documentos/repository.py` |
| `_CacheDocumentos` | Lista pública con TTL, hits/misses e invalidación | `app/documentos/repository.py` |
| `ProcesadorIdempotente` | Descarta por `event_id` | `app/eventos/outbox.py` |
| `despachar` / `_entregar` | Reintentos 1 s y 2 s y DLQ | `app/eventos/outbox.py` |
| `registrar_para_revision` | Consumidor: valida campos y evita duplicar por documento | `app/administracion/revision.py` |
| `exigir_token_admin` | Fail-closed y comparación en tiempo constante | `app/seguridad/autenticacion.py` |
| `_JsonFormatter` | Log JSON con correlación y campos de evento | `app/main.py` |
| Cabeceras de seguridad | CSP, HSTS, nosniff, frame-ancestors, referrer | `app/main.py` |

## 5.5 Qué no es un bloque

No hay broker, ni cola persistente, ni servicio de archivos, ni caché distribuida. Cuando se
introduzcan, entran como bloques nuevos con su ADR, no como una extensión silenciosa de los
actuales.
