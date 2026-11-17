# 11. Riesgos y deuda técnica

## 11.1 Riesgos técnicos

| # | Riesgo | Prob. | Impacto | Mitigación / estado | Dueño |
|---|---|---|---|---|---|
| R1 | Firestore no responde y la búsqueda queda degradada | Media | Alto | Timeout 2 s + 3 intentos + 503; caché sirve si está tibia. **Mitigado** | Backend |
| R2 | El outbox en memoria pierde eventos al reiniciar | Alta | Bajo/medio | Se declara en `docs/eventos/limites.md`; el documento persiste y la bandeja es reconstruible. **Aceptado** | Arquitectura |
| R3 | Dos instancias tendrían caché y bandeja separadas | Baja hoy | Alto si se escala | Despliegue de una instancia; criterio de reapertura en ADR 0013/0015. **Aceptado con límite** | Infraestructura |
| R4 | Sin autenticación de usuarios, el token administrativo no identifica personas | Alta | Medio | Token con fail-closed; reabrir con `usuarios` (ADR 0014). **Aceptado** | Seguridad |
| R5 | Sin rate limit, la API pública puede saturarse | Media | Medio | Límite de CPU/memoria del contenedor y caché; el plan gratuito es el techo. **Aceptado** | Infraestructura |
| R6 | La ventana entre comprobar la clave de idempotencia y crear no es atómica | Baja | Bajo | Reintento devuelve el documento; se documenta la ventana. **Aceptado** | Backend |
| R7 | Caché fría concurrente genera lecturas extra (*stampede*) | Media | Bajo | Medido (21/300); *single-flight* queda como mejora. **Conocido** | Backend |
| R8 | El despliegue no está verificado (HTTP 404 al 2026-11-16) | Alta | Alto para la entrega | Descriptor y healthchecks listos; verificación humana pendiente y declarada. **Abierto** | Equipo |
| R9 | Sin `node` local, el build de Next.js solo se valida en CI | Media | Medio | Lockfile actualizado a mano; CI construye. **Aceptado con verificación en CI** | Frontend |
| R10 | SonarCloud marca el Quality Gate en **ERROR** (`new_reliability_rating=3`, `new_security_rating=3`, medido el 2026-11-17) | Alta | Medio | Los hallazgos están listados en §11.5 y en `docs/seguridad/dependencias.md`; el paso de Sonar en CI es condicional y no bloquea. **Deuda aceptada y declarada**, no se afirma un gate en verde | Equipo |

## 11.2 Deuda técnica declarada

| Deuda | Por qué se acepta | Condición para pagarla |
|---|---|---|
| Subida y almacenamiento de archivos | El corte actual persiste metadatos; el archivo exige almacenamiento externo | Cuando se implemente el flujo completo de publicación con archivo |
| Calificaciones por usuario | `calificacion` es un atributo semilla; el módulo no tiene persistencia | ADR 0003, al entrar `calificaciones` en alcance |
| Autor como texto libre | `usuarios` no existe | Al implementar cuentas; migrar a `autor_id` |
| Bandeja y outbox en memoria | Una instancia, costo cero | Más de una instancia o evento que deba sobrevivir |
| Retención de datos personales | No hay datos reales todavía | Antes de abrir registro a estudiantes |
| SBOM | Lockfiles y hashes son el inventario actual | Cuando el curso o un cliente lo exija |
| Búsqueda de texto completo en Firestore | El filtrado en memoria es suficiente para el catálogo actual | Si el catálogo crece y el p95 se acerca al umbral |
| Sin pruebas de navegador | No hay runner de frontend; el comportamiento se revisa en código | Cuando se incorpore Playwright u equivalente |

## 11.3 Revisión de pares y hallazgos incorporados

Hallazgos recibidos en las revisiones de las semanas 9–14 y su estado **real** (no se marca
«resuelto» nada que no tenga artefacto verificable).

| # | Hallazgo | Acción tomada | Estado |
|---|---|---|---|
| H1 | Faltaban `Dockerfile`, descriptor de despliegue y pasos reproducibles | Se añadieron `Dockerfile`, `app/frontend/Dockerfile`, `docker-compose.yml` y `Dockploy/compose.lab.yml` con healthchecks y límites | **Cerrado en repositorio**; despliegue sin verificar |
| H2 | Brecha de ADR: no había registro de varias decisiones (persistencia, seguridad, eventos, medición) | ADR 0011–0016 creados con alternativas y consecuencias; 0004, 0008–0012 marcados como aceptados | **Cerrado** |
| H3 | La tabla de aspectos y el registro de IA estaban en rutas no canónicas | `docs/aspectos.md` y `docs/ia.md` son la fuente; las rutas antiguas quedan como redirección | **Cerrado** |
| H4 | arc42, C4 y README describían SQLite, Render y Vercel | Se reescribieron con Firestore, Docker/Dokploy, caché y outbox; el estado del despliegue se declara 404 | **Cerrado en documentos**; verificación de URL abierta |
| H5 | El indicador «≤ 3 interacciones» no era operacional para S10 | Se adoptó p95/error/lecturas con herramienta y línea base (ADR 0016) | **Cerrado** |
| H6 | No había evidencia de modos de fallo de la llamada real backend→Firestore | `docs/resiliencia/modos-de-fallo.md` reescrito; pruebas de timeout, reintento e idempotencia | **Cerrado con prueba** |
| H7 | El taller de mensajes podía quedar como descripción | Outbox real con contrato, deduplicación, reintentos, DLQ y pruebas | **Cerrado con código y pruebas** |
| H8 | La bandeja de revisión exponía nombres de autores sin credencial | `X-Admin-Token` obligatorio; OpenAPI 1.3.0 con cambio incompatible anotado | **Cerrado con prueba** |
| H9 | `next@14.2.15` estaba deprecado por seguridad | Subido a `14.2.35` en `package.json` y lockfile | **Cerrado en repositorio**; build en CI |
| H10 | El pipeline no era auditable en el remoto | Workflow completo con JUnit, `pip-audit`, `npm audit` y medición. Los runs #44–#47 fallaron **sin jobs** porque usaban `secrets` dentro de un `if` de paso, que GitHub rechaza al validar el workflow; en la copia local el token se expone como `env` de job y la condición usa `env.SONAR_TOKEN` | **Abierto** hasta empujar la corrección y ver el run en verde |
| H11 | SonarCloud sin evidencia de Quality Gate | Proyecto público en la organización `isco-utb`; `sonar.organization` corregido. El gate real está en **ERROR** y se declara con sus métricas | **Abierto** (deuda aceptada, ver §11.5) |
| H12 | Las URLs desplegadas no respondían | Se declaran 404 y no se usan como evidencia; verificación pendiente | **Abierto** (acción humana) |

Regla adoptada: un hallazgo solo pasa a «cerrado» cuando existe el archivo, la prueba o la corrida
que lo demuestra. Los que dependen de infraestructura o de una cuenta externa se quedan abiertos y
se dicen abiertos.

## 11.4 Modos de fallo de la integración principal

La integración principal es **backend → Firestore** (síncrona, en cada lectura o escritura) y su
continuación asíncrona **outbox → administración**. El detalle operativo está en
[`docs/resiliencia/modos-de-fallo.md`](../resiliencia/modos-de-fallo.md); aquí queda el resumen que
exige la ficha S11.

| Modo de fallo | Qué ocurre | Mitigación implementada | Qué se acepta | Evidencia |
|---|---|---|---|---|
| **No responde** | `firebase-admin` no contesta | Timeout 2 s por llamada, 3 intentos con espera creciente, 503 genérico al cliente; la caché tibia sigue sirviendo la búsqueda | Una escritura puede fallar con 503; el cliente reintenta con la misma `Idempotency-Key` | `tests/test_resiliencia.py`, `docs/resiliencia/modos-de-fallo.md` |
| **Responde tarde** | La llamada excede el timeout | El timeout corta la espera; no se bloquea el proceso más de lo presupuestado; la métrica registra la duración | Una respuesta tardía puede llegar después de haber devuelto 503 | `tests/test_resiliencia.py` |
| **Responde dos veces** | Reintento del cliente o entrega duplicada del evento | `Idempotency-Key` + hash del cuerpo (200 con el mismo documento, 409 si el cuerpo cambia); `ProcesadorIdempotente` descarta por `event_id` | La ventana entre comprobar la clave y crear no es atómica (R6); el evento puede perderse al reiniciar (R2) | `tests/test_idempotencia.py`, `tests/test_eventos.py` |

## 11.5 Amenazas aceptadas y deuda de análisis estático

Las amenazas con prioridad ≥ 8 que **no** se corrigen en este corte, con el motivo y la condición de
reapertura, están en [`docs/seguridad/amenazas.md`](../seguridad/amenazas.md):

| Amenaza | Por qué se acepta | Condición de reapertura |
|---|---|---|
| T1 / T5 / T12 (token administrativo compartido) | No hay cuentas de usuario; el token separa público de administración con `compare_digest` | Al implementar `usuarios` (ADR 0014) |
| T2 / T4 (autoría y contenido sin moderar) | La escritura exige token; la bandeja de revisión es posterior a la publicación | Registro abierto o contenido de terceros |
| T9 / T11 (sin *rate limit* ni WAF) | El plan gratuito y el límite de CPU/memoria del contenedor son el techo actual | Tráfico real o despliegue con dominio público estable |
| T15 (retención de datos personales) | No hay datos reales de estudiantes | Antes de abrir registro |

**Deuda de análisis estático.** El Quality Gate de SonarCloud está en **ERROR** con
`new_reliability_rating=3` y `new_security_rating=3` (consulta del 2026-11-17: 44 incidencias
abiertas, 29 de ellas en el sitio legado `shareuwensite-main/`). Se acepta y se declara en lugar de
ocultarla. Las correcciones locales pendientes de push son:

- `docker:S8541` / `S8544` en `Dockerfile` y `Dockploy/Dockerfile.api`, y `docker:S6505` en los dos
  Dockerfile web: instalaciones sin `--only-binary`/`--require-hashes`/`--ignore-scripts`.
  **Corregido en repositorio**; el CI ya instalaba con esas banderas.
- `pythonsecurity:S8703` / `S8707` en `scripts/medicion/bench_busqueda.py`: se añadieron validación
  de URL (http/https y hosts locales salvo permiso explícito) y confinamiento de la salida a
  `docs/evidencia/mediciones/`, con pruebas en `tests/test_bench_busqueda.py`.
- `python:S8410` en los routers de `administracion` y `documentos`: migrado a `Annotated`.
- `typescript:S9383` en `app/frontend/app/page.tsx`: promesas marcadas con `void`.
- Incidencias del sitio estático legado: no es el frontend canónico (ADR 0005); se recomienda
  excluirlo en la configuración del proyecto en SonarCloud.

Dueño: equipo. Condición para cerrar: token de SonarCloud configurado, análisis automático
desactivado a favor del scanner del workflow, correcciones empujadas y gate en verde sobre `master`.

## 11.6 Riesgo de entrega

El riesgo principal del corte no es técnico: es **presentar como verificado lo que no lo está**. Por
eso el README, §7 y esta sección repiten el estado 404, la ausencia de run remoto y los límites de
la medición local. La sustentación puede defender lo implementado sin atribuirse lo que falta.
