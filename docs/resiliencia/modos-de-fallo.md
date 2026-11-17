# Modos de fallo, idempotencia y saga — Evidencia S11

El sistema tiene **dos integraciones reales**, no una:

1. **Navegador → frontend Next.js → API FastAPI** (HTTP/JSON), que sirve la búsqueda y la
   publicación.
2. **API → Firestore** (firebase-admin), que es la llamada de red que domina el flujo desde que la
   persistencia dejó de ser SQLite en el mismo proceso (ADR 0012).

Además existe una integración **interna asíncrona**: `documentos` → outbox → `administracion`
(evento `documento.publicado`, ADR 0015). No es una llamada de red, pero tiene sus propios modos de
fallo y se trata al final.

## 1. Integración navegador → API

- Cliente: `app/frontend/lib/api.ts` (`buscarDocumentos`, `pedirConTimeout`, `pedirConReintento`) y
  `app/frontend/app/page.tsx` (`buscar`).
- Servidor: `app/busqueda/router.py` → `busqueda.service` → `documentos.service` (in-process).

| Modo | Causa concreta | Efecto sin mitigación | Mitigación implementada | Prueba |
|---|---|---|---|---|
| **No responde** | API caída o reiniciando; red del estudiante | La pantalla queda sin resultados | `catch` en `page.tsx` muestra «No se pudo conectar con el backend o tardó demasiado»; un reintento tras 1 s ante error de red o 5xx (`pedirConReintento`); `GET /health` para que la plataforma reinicie el contenedor | Sin prueba automatizada de frontend (no hay runner); el contrato de la respuesta sí está probado en `tests/test_contrato.py` |
| **Responde tarde** | Arranque en frío del contenedor o Firestore lento | «Buscando…» indefinido | Timeout de 15 s con `AbortController`; al vencer cuenta como «no responde» y entra al reintento; luego mensaje de error | Igual que arriba: comportamiento del cliente, verificado por revisión de código |
| **Responde dos veces** | Doble clic; reintento tras timeout cuando el primer intento sí llegó; doble efecto de React en desarrollo | Respuestas fuera de orden pisan el estado | La búsqueda es `GET` idempotente; `ultimaBusqueda` (ref) descarta respuestas obsoletas. Efecto aceptado: `registrar_busqueda` cuenta la repetición dos veces (métrica indicativa, ADR 0008) | `tests/test_resiliencia.py` (3 pruebas) |

## 2. Integración API → Firestore (el borde crítico)

- Código: `app/documentos/repository.py` (`_con_reintentos`, `_reservar_id_y_crear`,
  `_buscar_por_idempotencia`, `listar_documentos`).
- Timeout por intento: **2 s**; reintentos: **3** con espera creciente; el error final se traduce a
  `ErrorPersistencia` y la API responde **503**.

| Modo | Causa concreta | Efecto sin mitigación | Mitigación implementada | Prueba |
|---|---|---|---|---|
| **No responde** | Firestore inaccesible, credenciales ausentes o inválidas, cuota agotada | La búsqueda se cuelga o la publicación devuelve un error opaco | `_con_reintentos` con timeout de 2 s y 3 intentos; `ErrorPersistencia` → **503** con mensaje genérico; `/health` sigue respondiendo para distinguir «proceso vivo» de «dependencia caída» | `test_timeout_se_reporta_como_error_de_persistencia`; sin credenciales, el arranque no falla y las rutas de datos devuelven 503 |
| **Responde tarde** | Firestore lento o cold start del SDK | Se acumulan solicitudes y se agota el pool | Timeout por intento + reintentos acotados; la caché de lectura evita ir a Firestore en la mayoría de búsquedas (TTL 60 s) | `test_timeout_se_reporta_como_error_de_persistencia`; medición S14 |
| **Responde dos veces** | El cliente reintenta porque no recibió la respuesta, pero la escritura sí se aplicó | Documento duplicado | `Idempotency-Key` + hash SHA-256 del cuerpo: misma clave y mismo cuerpo → **200** con el documento existente; misma clave y cuerpo distinto → **409**. La reserva de id con `DocumentReference.create()` impide que dos escritores compartan id | `test_repetir_la_misma_clave_no_duplica`, `test_misma_clave_con_otro_cuerpo_devuelve_409`, `test_dos_publicaciones_no_repiten_id`, `test_reservar_id_salta_un_id_que_otro_escritor_tomo` |

### 2.1 La ventana que se acepta

La búsqueda por `idempotency_key` y el `create()` no son una sola transacción. Dos solicitudes
concurrentes con la misma clave y el mismo cuerpo pueden llegar a la vez: una crea (201) y la otra
recibe `AlreadyExists` o no encuentra la clave todavía y crea un segundo documento. El compromiso
declarado es que el cliente reintente con la misma clave: la comprobación posterior devuelve el
documento ya creado y el peor caso es un documento duplicado bajo una clave repetida en una
ventana de milisegundos. Se acepta para no introducir una transacción distribuida ni una colección
de bloqueos; queda como limitación en [`../datos/consistencia.md`](../datos/consistencia.md).

## 3. Idempotencia de las operaciones

| Operación | ¿Repetirla cambia el estado? | Mecanismo |
|---|---|---|
| `GET /busqueda/documentos` | No | Lectura pura; la métrica cuenta la repetición (efecto aceptado) |
| `POST /documentos` | No, con la misma `Idempotency-Key` y el mismo cuerpo | Clave única + hash; 200 en la repetición, 409 si el cuerpo cambió; sin segundo evento |
| Consumir `documento.publicado` | No | `ProcesadorIdempotente` por `event_id` + comprobación por `id_documento` |
| `POST /administracion/revision/{id}/resolver` | Sí en la segunda llamada devuelve 404 | La entrada se retira de la cola; repetir no encuentra el documento, lo que es un resultado correcto y observable (no un duplicado) |
| `GET /administracion/metricas`, `/cache`, `/eventos` | No | Lectura de contadores |

La publicación es la operación que la ficha S11 pide endurecer; su prueba de fuego es
`test_reintentar_la_publicacion_no_emite_un_segundo_evento`: repetir la publicación no vuelve a
poner el documento en la bandeja.

## 4. Saga: por qué no se usa

**No aplica hoy.** Publicar un documento es una sola escritura en Firestore. El segundo efecto
—ponerlo en la bandeja de revisión— es **recuperable y no compensable**: si no llega el aviso, el
documento sigue siendo válido y la bandeja se puede reconstruir; no hay que «deshacer» la
publicación. Por eso se usa un outbox con reintentos y no una saga con pasos de compensación
(ADR 0015). Una saga sería necesaria si existiera, por ejemplo, «guardar archivo en un
almacenamiento externo + registrar metadatos»: ahí el paso 2 podría fallar y el paso 1 habría que
compensarlo borrando el archivo. Ese flujo **no está implementado**; cuando entre en alcance, la
saga mínima será archivo primero, metadatos después, y compensación por borrado.

## 5. Integración interna: outbox → bandeja de revisión

| Modo | Causa | Efecto | Mitigación | Prueba |
|---|---|---|---|---|
| **No responde** | El consumidor lanza una excepción | El documento se publica igual; la bandeja no lo recibe | Reintentos 1 s y 2 s; luego DLQ en memoria | `test_un_fallo_recuperable_se_reintenta_y_termina_bien`, `test_agotar_los_intentos_manda_el_evento_a_fallidos` |
| **Responde tarde** | Consumidor lento | La respuesta HTTP ya se envió (`BackgroundTasks`) | El despacho ocurre después de responder; no bloquea al estudiante | `test_publicar_entrega_el_evento_al_consumidor` |
| **Responde dos veces** | Reentrega «al menos una vez» | Dos entradas de revisión | Deduplicación por `event_id` y por `id_documento` | `test_un_duplicado_no_crea_dos_entradas_de_revision` |

Los límites de durabilidad (reinicio pierde pendientes) están en
[`../eventos/limites.md`](../eventos/limites.md).

## 6. Resumen para la sustentación

- **Con prueba automatizada:** «responde dos veces» en frontend→API; los tres modos de
  API→Firestore; los tres modos del outbox.
- **Implementado y verificado por revisión, sin runner propio:** «no responde» y «responde tarde»
  del frontend (requiere un runner de pruebas de navegador, fuera del alcance del corte).
- **Aceptado como limitación:** la ventana no atómica entre comprobar la clave y crear; la falta de
  durabilidad del outbox; la ausencia de rate limit.

## 7. Trazabilidad

`docs/aspectos.md` (A3, A4) → [ADR 0004](../adr/0004-integracion-sincrona-y-asincrona.md),
[ADR 0011](../adr/0011-identidad-de-datos-y-propiedad-por-modulo.md),
[ADR 0015](../adr/0015-mensajeria-asincrona-con-outbox.md) → `app/documentos/repository.py`,
`app/eventos/outbox.py` → `tests/test_resiliencia.py`, `tests/test_idempotencia.py`,
`tests/test_eventos.py` → este documento → `docs/evidencia/s11-fallos-parciales.md`.
