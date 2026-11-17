# 8. Conceptos transversales

## 8.1 Dominio y fronteras

El lenguaje y la propiedad de datos están en [`../ddd/contextos.md`](../ddd/contextos.md),
[`../ddd/propiedad-datos.md`](../ddd/propiedad-datos.md) y
[`../ddd/auditoria-violaciones.md`](../ddd/auditoria-violaciones.md). La regla operativa: cada dato
tiene **un solo módulo escritor** y los demás lo piden por su interfaz de servicio. Las violaciones
detectadas (calificación dentro de documentos, autor como texto libre) están registradas con su plan
y su ADR 0003; no se ocultan.

## 8.2 Persistencia

- Motor: **Firestore** (ADR 0012), encapsulado en `app/documentos/repository.py`. Es el único lugar
  que conoce `firebase-admin`.
- Colección `documentos`; el id del documento es el entero del dominio convertido a texto.
- Los campos internos (`idempotency_key`, `idempotency_hash`, `creado_en`) se excluyen de toda
  respuesta pública con `_CAMPOS_INTERNOS` y `_publico`.
- Sin credenciales, la inicialización no bloquea el arranque: `/health` responde y las rutas de
  datos devuelven 503.
- No hay migraciones ni ORM: el esquema es el diccionario que valida Pydantic antes de escribir.

## 8.3 Consistencia, idempotencia y caché

| Aspecto | Decisión | Detalle |
|---|---|---|
| Unicidad del id | `DocumentReference.create()` atómico + reintento con el siguiente candidato | ADR 0011 |
| Idempotencia de publicar | `Idempotency-Key` + SHA-256 del cuerpo; 200/409 | §2 de `docs/resiliencia/modos-de-fallo.md` |
| Lectura | Caché en proceso, TTL 60 s, invalidación tras escritura | ADR 0013 |
| Lectura entre instancias | Eventual, acotada por el TTL | Solo hay una instancia |
| Evento | Al menos una vez + deduplicación por `event_id` | ADR 0015 |
| Bandeja | En memoria, protegida por lock; se vacía al reiniciar | Límite declarado |

La tabla completa operación → garantía está en [`../datos/consistencia.md`](../datos/consistencia.md).

## 8.4 Mensajería y eventos

Contrato en [`../eventos/contrato-evento.md`](../eventos/contrato-evento.md), esquema en
`documento-publicado.schema.json`, límites en [`../eventos/limites.md`](../eventos/limites.md). El
productor no conoce al consumidor: la suscripción se hace en `app/main.py`. La entrega es al menos
una vez; el consumidor deduplica. Los reintentos son 1 s y 2 s y luego DLQ en memoria.

## 8.5 Contrato de API

`docs/api/openapi.yaml` es la fuente única de verdad (versión **1.3.0**). `tests/test_contrato.py`
valida las respuestas reales contra el esquema. El cambio de esta versión —exigir token en la
bandeja de revisión— es **incompatible a propósito** y está anotado en el historial del contrato.
Regla: un campo eliminado, renombrado o con otro tipo exige versión nueva y consumidor nuevo.

## 8.6 Seguridad

- `X-Admin-Token` para `POST /documentos`, `GET /administracion/revision` y
  `POST /administracion/revision/{id}/resolver`.
- Fail-closed: sin `SHAREU_ADMIN_TOKEN`, 503; token ausente o distinto, 401.
- Comparación con `secrets.compare_digest` (tiempo constante).
- CORS explícito, nunca `*`; cabeceras CSP, HSTS, nosniff, frame-ancestors y referrer.
- Errores genéricos al cliente; detalle solo en logs.
- El modelo de amenazas y su priorización están en [`../seguridad/amenazas.md`](../seguridad/amenazas.md).

## 8.7 Privacidad

Solo se guarda el **nombre del autor**. No se registran cuerpos de solicitud, cabeceras de
autorización ni IPs. La bandeja de revisión, que muestra nombres y material pendiente, exige token.
La retención automática es trabajo pendiente antes de operar con datos reales; se declara en
`docs/seguridad/amenazas.md` §4.

## 8.8 Observabilidad

| Señal | Dónde | Campos |
|---|---|---|
| Log por solicitud | `stdout`, formato JSON | `request_id`, `method`, `path`, `status_code`, `duration_ms` |
| Log de evento | `stdout` | `event_id`, `correlation_id`, `tipo_evento`, `intento`, `estado_evento`, `espera_segundos` |
| Salud | `GET /health` | `{"estado":"ok"}` |
| Caché | `GET /documentos/cache`, `GET /administracion/cache` | `ttl_segundos`, `entradas`, `hits`, `misses`, `invalidaciones` |
| Eventos | `GET /administracion/eventos` | `pendientes`, `procesados`, `duplicados`, `reintentos`, `fallidos` |
| Métricas de uso | `GET /administracion/metricas` | `total_busquedas`, `tasa_busquedas_sin_resultados` |

El `request_id` se propaga como `correlation_id` al evento, de modo que una publicación se puede
seguir desde la solicitud HTTP hasta el consumo en la bandeja.

## 8.9 Validación y errores

- Pydantic valida el cuerpo y los parámetros; `calificacion` entre 0 y 5; longitudes máximas.
- 400/422: entrada inválida. 401: falta o no coincide el token. 409: conflicto de idempotencia.
  404: revisión inexistente. 503: persistencia no disponible o configuración ausente.
  500: error inesperado, con mensaje genérico y detalle solo en el log.
- El frontend distingue 4xx (no reintenta) de 5xx o error de red (un reintento).

## 8.10 Configuración

| Variable | Efecto | Defecto seguro |
|---|---|---|
| `FIREBASE_CREDENTIALS_JSON` | Credenciales de la cuenta de servicio | Sin ella, 503 en datos; `/health` sigue |
| `SHAREU_ADMIN_TOKEN` | Token administrativo | Sin ella, 503 en rutas protegidas |
| `SHAREU_FRONTEND_ORIGIN` | Orígenes CORS separados por coma | Los dos de Next.js en local |
| `SHAREU_CACHE_TTL_SEGUNDOS` | TTL de la caché; `0` la apaga | 60 |
| `SHAREU_EVENTO_ESPERA_BASE_SEGUNDOS` | Base de la espera exponencial | 1,0 |

## 8.11 Pruebas

`pytest -q` cubre contrato, fronteras, búsqueda, usabilidad, caché, idempotencia, eventos,
resiliencia, seguridad y el esqueleto de módulos. Las pruebas usan un Firestore falso en
`tests/firestore_falso.py`; no necesitan credenciales. CI ejecuta además la medición en modo ASGI y
publica el artefacto.
