# Modelado de amenazas (STRIDE) — Evidencia S13

El modelo se aplica sobre el C4 nivel 2 real: navegador → frontend Next.js → API FastAPI →
Firestore, más el outbox en proceso y la credencial administrativa. No se modelan componentes
inexistentes (no hay broker, no hay autenticación de usuarios, no hay almacenamiento de archivos
todavía); cuando existan, este documento se reabre.

## 1. Superficie de ataque

| Elemento | Dónde vive | Qué expone |
|---|---|---|
| `GET /busqueda/documentos` | API pública | Lectura de metadatos públicos; filtros |
| `POST /documentos` | API protegida | Escritura de metadatos en Firestore |
| `GET /administracion/revision` | API protegida | Nombres de autores y material pendiente |
| `POST /administracion/revision/{id}/resolver` | API protegida | Retiro de la bandeja |
| `GET /administracion/eventos`, `/cache`, `/metricas` | API pública | Contadores internos (sin datos personales) |
| `GET /docs`, `/redoc`, `/openapi.json` | API pública | Forma de la API; no datos |
| Cuenta de servicio de Firebase | Variable `FIREBASE_CREDENTIALS_JSON` | Acceso total a Firestore |
| `X-Admin-Token` | Cabecera HTTP | Separa público de administración |
| Outbox y bandeja | Memoria del proceso | Estado efímero |

## 2. Amenazas, probabilidad, impacto y prioridad

Escala: probabilidad e impacto **1–5**; prioridad = probabilidad × impacto (1–25). Un riesgo con
prioridad ≥ 12 exige mitigación en este corte o aceptación explícita con dueño.

| # | STRIDE | Amenaza | Prob. | Imp. | Prioridad | Mitigación implementada | Riesgo residual | Dueño | Estado |
|---|---|---|---|---|---|---|---|---|---|
| T1 | **S**poofing | Un cliente se hace pasar por administrador para publicar | 3 | 4 | 12 | `X-Admin-Token` con `secrets.compare_digest`; fail-closed 503 si no está configurado | Token compartido: no identifica personas | Seguridad | **Mitigado parcialmente, aceptado** |
| T2 | **S**poofing | Suplantar a un estudiante al publicar o calificar | 2 | 4 | 8 | No hay cuentas todavía; la escritura exige token administrativo | Sin identidad de usuario, no hay autoría verificable | Arquitectura | **Aceptado; se reabre con `usuarios`** |
| T3 | **T**ampering | Alterar documentos en Firestore desde el cliente | 1 | 5 | 5 | El cliente nunca habla con Firestore: solo con la API; la cuenta de servicio es del backend | Si se filtran credenciales, el atacante tiene acceso total | Seguridad | **Mitigado por diseño** |
| T4 | **T**ampering | Inyectar contenido malicioso en `titulo`, `materia`, `palabras_clave` | 3 | 3 | 9 | Validación Pydantic (longitud y tipo); el frontend escapa el texto al renderizar (React) | No hay moderación de contenido antes de publicar; la bandeja es posterior | Producto | **Aceptado con moderación pendiente** |
| T5 | **R**epudiation | Un administrador niega haber publicado o resuelto | 3 | 2 | 6 | `request_id` y `correlation_id` en logs; log de publicación y de evento | No se registra *quién*: el token es compartido | Operación | **Aceptado hasta `usuarios`** |
| T6 | **I**nformation disclosure | Leer la bandeja de revisión sin credencial | 3 | 4 | 12 | `GET /administracion/revision` exige token (cambio incompatible de OpenAPI 1.3.0) | Logs y métricas no exponen la bandeja | Seguridad | **Mitigado** |
| T7 | **I**nformation disclosure | Fuga de secretos en el repositorio o en logs | 2 | 5 | 10 | `.env` fuera de git; `git grep` de credenciales en la verificación; logs sin cuerpo ni cabeceras | Un `git push` accidental sigue siendo posible | Seguridad | **Mitigado con revisión manual** |
| T8 | **I**nformation disclosure | Mensajes de error revelan detalles internos | 3 | 2 | 6 | 503 genérico en persistencia; 500 genérico en el middleware; sin traza al cliente | Los logs internos sí contienen detalle | API | **Mitigado** |
| T9 | **D**enial of service | Saturar `GET /busqueda/documentos` con tráfico | 3 | 3 | 9 | Caché de lectura (TTL 60 s) reduce lecturas; contenedor con límite de 0,5 CPU y 256 MB | **No hay rate limit** ni WAF; el plan gratuito es el techo | Infraestructura | **Aceptado con límite declarado** |
| T10 | **D**enial of service | Llenar el outbox publicando en bucle | 2 | 2 | 4 | `POST /documentos` exige token; la caché no interviene | El outbox no tiene backpressure | Backend | **Aceptado (requiere token)** |
| T11 | **E**levation of privilege | Usar el token administrativo para leer la bandeja desde otro origen | 2 | 4 | 8 | CORS explícito sin `*`; la cabecera no se expone al navegador salvo en la petición | CORS no protege contra clientes que no son navegador; el token es la barrera real | Seguridad | **Mitigado parcialmente** |
| T12 | **E**levation of privilege | Escalar de lectura pública a escritura | 2 | 4 | 8 | Rutas de escritura separadas y protegidas; Firestore no se expone al cliente | Si el token se filtra, la barrera desaparece | Seguridad | **Mitigado parcialmente** |
| T13 | **S**poofing (transporte) | Interceptar tráfico entre frontend y API | 2 | 4 | 8 | HTTPS en Dokploy; HSTS cuando `X-Forwarded-Proto=https` | En local no hay TLS, es esperado | Infraestructura | **Mitigado en producción** |
| T14 | **T**ampering (evento) | Alterar el payload de `documento.publicado` | 1 | 3 | 3 | El evento no sale del proceso; el contrato valida campos obligatorios | Un consumidor futuro externo necesitará autenticación de mensajes | Backend | **Aceptado (in-process)** |
| T15 | **I**nformation disclosure | Ver datos personales en la consola de Firebase | 2 | 3 | 6 | Acceso restringido a la cuenta de servicio y a la consola del proyecto | Sin política de retención formal todavía | Datos | **Aceptado; ver §4** |

## 3. Prioridades y decisiones

- **Prioridad ≥ 12:** T1 (token administrativo) y T6 (bandeja protegida). T1 se mitiga con token
  y se **acepta** el residual de identidad; T6 está **mitigado**.
- **Prioridad 8–11:** T2, T7, T9, T11, T12, T13. T7 y T13 están mitigados; T9 y T11 se aceptan con
  límite declarado; T2 y T12 se reabren cuando exista `usuarios`.
- **Prioridad ≤ 7:** T3, T4, T5, T8, T10, T14, T15. Se aceptan o están mitigados por diseño.

## 4. Privacidad

| Pregunta | Respuesta en ShareU |
|---|---|
| ¿Qué datos personales se tratan? | **Nombre del autor** del documento (`payload.autor`, `documentos.autor`). No hay correo, teléfono, documento de identidad ni IP almacenada |
| ¿Dónde se almacenan? | Firestore, colección `documentos`; en la bandeja de revisión solo en memoria mientras el proceso vive |
| ¿Se registran en logs? | **No.** El log estructurado guarda `request_id`, método, ruta, estado y duración; **no** el cuerpo, **no** la cabecera `X-Admin-Token` y **no** la IP |
| ¿Se exponen al público? | El nombre del autor aparece en los resultados de búsqueda (es parte del material). La bandeja de revisión, que también lo muestra, exige token |
| ¿Base legal / finalidad? | Finalidad académica: atribuir el material a su autor. El proyecto es un ejercicio universitario, no un servicio comercial |
| ¿Retención? | Sin política automática todavía: los documentos permanecen hasta que se eliminen manualmente. **Trabajo pendiente** antes de operar con datos reales |
| ¿Derechos de los titulares? | Al no haber cuentas, el canal es el equipo administrador. Se documentará cuando exista `usuarios` |
| ¿Minimización? | `_CAMPOS_INTERNOS` y `_publico` excluyen `idempotency_key`, `idempotency_hash` y `creado_en` de las respuestas públicas; el evento solo lleva autor, título y materia |

Riesgo de privacidad principal: **no hay identidad de usuario ni retención formal**. Se acepta
mientras el sistema no reciba datos reales de estudiantes; es condición de reapertura antes de
abrir el registro.

## 5. Cómo se verificó

- `tests/test_seguridad.py`: cabeceras de endurecimiento, CORS y ausencia de `*`.
- `tests/test_idempotencia.py`: escritura apagada sin token (503), token inválido (401).
- `tests/test_eventos.py`: bandeja sin token rechazada y con token aceptada.
- `tests/test_bench_busqueda.py`: el banco de medición rechaza esquemas no HTTP, hosts externos sin
  permiso explícito y rutas de salida fuera de `docs/evidencia/mediciones/` (T9/T11 y S8703/S8707).
- Barrido de secretos con `git grep -nIiE '(api[_-]?key|secret|passw(or)?d|token|bearer|BEGIN (RSA|OPENSSH|PRIVATE)|ghp_|sk-)'`:
  no aparecen claves privadas, tokens ni `.env`. Sí aparece `apiKey` en
  `shareuwensite-main/firebase-config.js`: es la **configuración web** de Firebase, pública por
  diseño y sin permiso propio sobre Firestore; la barrera real son las reglas del proyecto y la
  restricción de la clave por *referrer*, que queda como acción pendiente en Google Cloud.
- `pip-audit` limpio; `npm audit` y Dependabot en CI (ver [`dependencias.md`](dependencias.md)).

## 6. Trazabilidad

`docs/aspectos.md` (A5, A9) → [ADR 0014](../adr/0014-endurecimiento-http-y-escritura-autenticada.md)
→ `app/seguridad/autenticacion.py`, `app/main.py`, `app/administracion/router.py` →
`tests/test_seguridad.py`, `tests/test_eventos.py` → este documento →
[`dependencias.md`](dependencias.md) → `docs/evidencia/s13-amenazas.md`.
