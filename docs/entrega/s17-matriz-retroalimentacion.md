# S17 · Matriz de retroalimentación y cierre arquitectónico

| | |
|---|---|
| Ficha | `arqsw:cierre` (semana 17) |
| Repositorio | `ISCOUTB/AS_202620_ShareU`, rama `master` |
| Estado comparado en S16 | [`e129842`](https://github.com/ISCOUTB/AS_202620_ShareU/commit/e1298422516716cdd168ec65baba42b979fbc7c0) · 2026-11-16T21:17:49-05:00 |
| Estado de esta entrega | commit de cierre (**pendiente de push**, ver §7) |
| Insumos | Retroalimentación publicada del docente; hallazgos H1–H12 de las revisiones de pares (arc42 §11.3); formulario del jurado **no disponible** |
| Documento guía S16 | [`final-guia-tres-paginas.md`](final-guia-tres-paginas.md) |
| Evidencia S16 | [`s16-evidencia-final.md`](s16-evidencia-final.md) |

## 0. Insumos recibidos y su disponibilidad

La ficha pide cotejar la matriz contra el formulario «Recomendaciones del jurado» y las revisiones
entre pares de la semana 14. El estado real de esos insumos es:

| Insumo | Disponibilidad | Qué se hizo |
|---|---|---|
| Formulario «Recomendaciones del jurado» | **No disponible**: no está en el repositorio ni en la información pública del curso; la API de GitHub registra 0 comentarios de revisión y 0 revisiones en los PR | Se declara como insumo faltante. **No se inventa** ninguna recomendación del jurado |
| Revisiones entre pares (semanas 9–14) | Disponibles como 12 hallazgos H1–H12 documentados en [`arc42 §11.3`](../arc42/11-riesgos-y-deuda-tecnica.md) | Se incorporan como filas `PAR-01`–`PAR-12` con su origen |
| Retroalimentación del docente | Publicada en `ISCOUTB/AS_202620_feedback` (`feedback.md`, seguimientos del 17/11 y evaluación S13/S14/S15) | Se convierte en las filas `DOC-01`–`DOC-17` |
| Requisito de revisión cruzada de la ficha S16 | 0 comentarios de *review* en la API de GitHub al 2026-11-21 | Se declara en `OTR-01` como aplazado, no como cumplido |

**Recuento.** 30 recomendaciones documentadas y clasificadas: **25 aceptadas, 3 aplazadas y 2
rechazadas**. Las del jurado no se pueden contar porque el formulario no existe en las fuentes
disponibles; esa diferencia se declara en lugar de rellenarse con suposiciones.

## 1. Matriz · retroalimentación del docente

Origen `DOC`: `feedback.md` del proyecto, seguimientos del 4, 5 y 17 de noviembre de 2026 y
`evaluacion-s13-s14-s15-2026-11-17.md`.

| ID | Origen y fecha | Recomendación recibida (resumen fiel) | Clasificación | Justificación técnica y acción | Evidencia | Commit / PR / ADR |
|---|---|---|---|---|---|---|
| DOC-01 | Seguimientos 20–26/10 y 17/11 | Publicar en el README la URL oficial `iscoutb.dev`, distinguiendo frontend y API | **Aceptada** | El README lista ambas URLs con estado HTTP comprobado y la búsqueda declarada en 500. Ya no hay *placeholders* Vercel/Render | [`README.md`](../../README.md) §Estado del despliegue; [`openapi.yaml`](../api/openapi.yaml) `servers` | Commit de cierre; comprobación 2026-11-21T22:19:51Z |
| DOC-02 | Seguimientos 04/11, 05/11 y 17/11 | Unificar rutas reales de Dockerfiles y compose; precisar qué frontend se publica; corregir `compose.lab.yml` frente a `.yaml` | **Aceptada** | Se corrigieron todas las referencias a `.yaml` (10 en el árbol y 4 en los ADR); el contenedor `web` construye `app/frontend` (Next.js) y el sitio estático queda como legado no desplegado | [`Dockerfile`](../../Dockerfile), [`docker-compose.yml`](../../docker-compose.yml), [`Dockploy/compose.lab.yaml`](../../Dockploy/compose.lab.yaml) | Commit de cierre; ADR 0005 |
| DOC-03 | Seguimiento 26/10 | Conciliar README, C4 y ADR con Firestore y retirar la descripción de SQLite | **Aceptada** | arc42 §2/§7, C4 y README describen Firestore; el ADR 0006 apunta al 0012. SQLite solo sobrevive como decisión histórica reemplazada | [`arc42/02`](../arc42/02-restricciones-arquitectonicas.md), [`arc42/07`](../arc42/07-vista-de-despliegue.md), [`c4/`](../c4/) | ADR 0006 → [ADR 0012](../adr/0012-persistencia-en-firestore.md); `e129842` |
| DOC-04 | S10 | La prueba de contrato anunciada debe cargar el OpenAPI, resolver referencias y validar respuestas e inválidos | **Aceptada** | `tests/test_contrato.py` carga el YAML, resuelve `$ref` y valida respuestas reales; se rompió a propósito para verla fallar | [`tests/test_contrato.py`](../../tests/test_contrato.py) | PR [#11](https://github.com/ISCOUTB/AS_202620_ShareU/pull/11), [#12](https://github.com/ISCOUTB/AS_202620_ShareU/pull/12) |
| DOC-05 | S12 | Tabla operación→garantía, caché con invalidación, ADR del mayor costo de reversión y consolidación en arc42 §8 | **Aceptada** | `docs/datos/consistencia.md` declara las garantías; la caché invalida tras escribir y se prueba; ADR 0013 compara alternativas | [`consistencia.md`](../datos/consistencia.md), [`test_cache.py`](../../tests/test_cache.py) | [ADR 0013](../adr/0013-cache-de-lectura-con-invalidacion.md) |
| DOC-06 | S11 | Tres modos de fallo con mitigación, diseño de idempotencia y evaluación de extracción con criterios | **Aceptada** | Modos «no responde / tarde / dos veces» con timeout, reintentos y hash; ADR 0010 evalúa no extraer con criterios de reapertura | [`modos-de-fallo.md`](../resiliencia/modos-de-fallo.md), [`test_idempotencia.py`](../../tests/test_idempotencia.py) | [ADR 0010](../adr/0010-no-extraer-modulos.md) |
| DOC-07 | S13 | STRIDE priorizado con dueño y estado; auditoría de dependencias en el pipeline con hallazgos revisados | **Aceptada** | Amenazas priorizadas por probabilidad×impacto; `pip-audit` y `npm audit` en el workflow; hallazgos D1–D9 decididos | [`amenazas.md`](../seguridad/amenazas.md), [`dependencias.md`](../seguridad/dependencias.md) | Commit de cierre |
| DOC-08 | S13 | Sección de privacidad con los datos personales tratados y su base | **Aceptada** | Se declara solo el nombre del autor, sin cuerpos ni IPs en logs, con retención y condición de reapertura | [`amenazas.md`](../seguridad/amenazas.md) §Privacidad; fila A9 de [`aspectos.md`](../aspectos.md) | [ADR 0014](../adr/0014-endurecimiento-http-y-escritura-autenticada.md) |
| DOC-09 | 17/11 | Habilitar SonarCloud en el pipeline y dejar de omitirlo | **Aceptada** | El token pasa a `env` del job y la condición usa `env.SONAR_TOKEN` (el contexto `secrets` no es fiable en un `if`). Se corrigieron las 33 incidencias abiertas en local; el gate sigue en ERROR hasta el reanálisis y se declara | [`.github/workflows/tests.yml`](../../.github/workflows/tests.yml), [`sonar-project.properties`](../../sonar-project.properties) | Commit de cierre |
| DOC-10 | 17/11 | Reconciliar issues con los cambios fusionados (#20 tras #23; #15 pedía C4 nivel 3) | **Aceptada** | Se creó el C4 nivel 3 que pedía #15 y #20 ya está implementado por #23. El cierre de los issues en GitHub se hace tras el push; su estado no es evidencia de implementación | [`c4/nivel-3.md`](../c4/nivel-3.md) | PR [#23](https://github.com/ISCOUTB/AS_202620_ShareU/pull/23) |
| DOC-11 | 17/11 | Añadir una corrida de medición contra el despliegue | **Aplazada** | Depende de dos acciones humanas: cargar `FIREBASE_CREDENTIALS_JSON` en Dokploy y redesplegar el 503. Medir hoy el endpoint devolvería 500 y no el flujo de búsqueda. Reapertura: búsqueda desplegada en 200 | [`s16-evidencia-final.md`](s16-evidencia-final.md) §2 | Ver §7 |
| DOC-12 | 17/11 | La medición publicada es local ASGI y no rendimiento demostrado del despliegue | **Aceptada** | Se declara el límite en arc42 §10, README, guía S16 y fila A2; no se extrapola al servidor | [`arc42/10`](../arc42/10-requisitos-de-calidad.md) §10.2 | `e129842` |
| DOC-13 | 17/11 | Comprobar la publicación y la respuesta servida de los dos dominios | **Aceptada** | Comprobación del 2026-11-21: web 200, `/health` 200, 404 y 503 correctos; la búsqueda responde 500 por falta de credenciales y se declara | [`s16-evidencia-final.md`](s16-evidencia-final.md) §2 | Verificación con `X-Request-Id` |
| DOC-14 | Ficha S16 | Entregar una guía de tres páginas con sistema, flujos, errores y desafío | **Aceptada** | Guía de tres páginas con verificación viva, flujos, caminos de error, medición y alcance declarado | [`final-guia-tres-paginas.md`](final-guia-tres-paginas.md) | Commit de cierre |
| DOC-15 | S16 / S17 | El estado calificado debe ser identificable y posterior al proyecto final | **Aceptada** | Se fija `e129842` como estado S16 y se documenta el diff de cierre; el hash final se escribe al empujar | [`s16-evidencia-final.md`](s16-evidencia-final.md) §1 | Ver §7 |
| DOC-16 | S10 (comentario preliminar) y 17/11 | Usar el MVP desplegado como **única** fuente de la medición del umbral | **Rechazada** | No es reproducible: depende de red externa, del arranque en frío del plan gratuito y, al 2026-11-21, del estado de configuración del servidor. Tampoco aísla el efecto del TTL, que es la variable del experimento. Se conserva la corrida local ASGI como evidencia del atributo y se añadirá la del despliegue como complemento, no como sustituto | [`s14-medicion.md`](../evidencia/s14-medicion.md) | [ADR 0016](../adr/0016-medicion-de-latencia-y-costo-de-lecturas.md) |
| DOC-17 | 04/11 y 17/11 | Publicar el sitio estático `shareuwensite-main/` como frontend oficial para que coincida con las capturas | **Rechazada** | Duplicaría el producto: el frontend canónico es Next.js (ADR 0005) y el sitio estático repite búsqueda y publicación con otra pila. Publicarlo reabriría los 29 hallazgos de Sonar ya corregidos y dejaría dos flujos que mantener. Se conserva como legado no desplegado y se declara | [`arc42/07`](../arc42/07-vista-de-despliegue.md), [`adr/0005`](../adr/0005-migracion-frontend-nextjs.md) | [ADR 0005](../adr/0005-migracion-frontend-nextjs.md) |

## 2. Matriz · hallazgos de la revisión entre pares

Origen `PAR`: hallazgos H1–H12 de [`arc42 §11.3`](../arc42/11-riesgos-y-deuda-tecnica.md),
recibidos en las revisiones de las semanas 9–14.

| ID | Hallazgo (H) | Clasificación | Justificación técnica y acción | Evidencia | Commit / PR / ADR |
|---|---|---|---|---|---|
| PAR-01 | H1 · Faltaban Dockerfile, descriptor y pasos reproducibles | **Aceptada** | Se añadieron los tres Dockerfile, `docker-compose.yml` y `Dockploy/compose.lab.yaml` con healthchecks y límites. El despliegue está activo; la búsqueda sigue pendiente de credenciales | [`Dockerfile`](../../Dockerfile), [`compose.lab.yaml`](../../Dockploy/compose.lab.yaml) | `e129842`; [ADR 0006](../adr/0006-plataforma-backend-despliegue.md) |
| PAR-02 | H2 · Brecha de ADR en persistencia, seguridad, eventos y medición | **Aceptada** | ADR 0011–0016 con alternativas y consecuencias; los aceptados que cambiaron quedaron con puntero de reemplazo | [`docs/adr/`](../adr/) | ADR 0011–0016 |
| PAR-03 | H3 · Aspectos y registro de IA en rutas no canónicas | **Aceptada** | `docs/aspectos.md` y `docs/ia.md` son la fuente; las rutas antiguas son redirecciones y el validador exige las canónicas | [`aspectos.md`](../aspectos.md), [`ia.md`](../ia.md) | Commit de cierre |
| PAR-04 | H4 · arc42, C4 y README describían SQLite, Render y Vercel | **Aceptada** | Se reescribieron con Firestore, Docker/Dokploy, caché y outbox; el estado del despliegue dejó de ser un 404 sin verificar | [`arc42/`](../arc42/00-portada.md), [`c4/`](../c4/) | `e129842` |
| PAR-05 | H5 · «≤ 3 interacciones» no era operacional | **Aceptada** | Se adoptó p95, tasa de error y lecturas por búsqueda, con herramienta, línea base y umbral en un solo lugar | [`bench_busqueda.py`](../../scripts/medicion/bench_busqueda.py) | [ADR 0016](../adr/0016-medicion-de-latencia-y-costo-de-lecturas.md) |
| PAR-06 | H6 · Sin evidencia de fallos backend→Firestore | **Aceptada** | Timeout 2 s, tres intentos y 503; las pruebas cubren timeout, reintento y recuperación | [`test_resiliencia.py`](../../tests/test_resiliencia.py), [`test_idempotencia.py`](../../tests/test_idempotencia.py) | Commit de cierre |
| PAR-07 | H7 · El taller de mensajes podía quedar como descripción | **Aceptada** | Outbox real con contrato, deduplicación por `event_id`, reintentos 1 s/2 s y DLQ | [`outbox.py`](../../app/eventos/outbox.py), [`test_eventos.py`](../../tests/test_eventos.py) | [ADR 0015](../adr/0015-mensajeria-asincrona-con-outbox.md) |
| PAR-08 | H8 · La bandeja de revisión exponía autores sin credencial | **Aceptada** | `X-Admin-Token` obligatorio con fail-closed; el cambio incompatible se anotó en OpenAPI | [`autenticacion.py`](../../app/seguridad/autenticacion.py) | [ADR 0014](../adr/0014-endurecimiento-http-y-escritura-autenticada.md) |
| PAR-09 | H9 · `next@14.2.15` deprecado por seguridad | **Aceptada** | Subido a `14.2.35` en `package.json` y lockfile; el build real se valida en CI porque el equipo no tiene Node local | [`package.json`](../../app/frontend/package.json) | Commit `c2f848b` |
| PAR-10 | H10 · Pipeline no auditable en el remoto | **Aceptada** | Workflow con JUnit, `pip-audit`, `npm audit`, medición y validación documental. Los runs fallidos sin jobs usaban `secrets` dentro de un `if`; ya se corrigió en local | [`.github/workflows/tests.yml`](../../.github/workflows/tests.yml) | Commit de cierre |
| PAR-11 | H11 · SonarCloud sin evidencia de Quality Gate | **Aceptada** | Proyecto público en `isco-utb`; organización corregida; 33 incidencias corregidas en local. El gate está en ERROR y se publica con sus métricas, sin afirmar que está en verde | [`arc42/11`](../arc42/11-riesgos-y-deuda-tecnica.md) §11.5 | Commit de cierre |
| PAR-12 | H12 · Las URLs desplegadas no respondían | **Aplazada** | La parte de disponibilidad está cerrada: web 200 y `/health` 200. La parte de **flujo de datos verificado** sigue abierta porque la instancia no tiene credenciales de Firestore y el equipo no tiene acceso a los logs del servidor. Reapertura: cargar credenciales y comprobar búsqueda y publicación en vivo | [`s16-evidencia-final.md`](s16-evidencia-final.md) §2 | Ver §7 |

## 3. Matriz · otros requisitos recibidos

| ID | Origen | Requisito | Clasificación | Justificación | Evidencia |
|---|---|---|---|---|---|
| OTR-01 | Ficha S16 y `CONTRATO.md` | Revisión cruzada con comentarios de fondo en los PR | **Aplazada** | La API de GitHub registra 0 comentarios y 0 revisiones: no depende del código ni de este equipo, sino de que otro equipo revise. No se presenta como cumplido. Reapertura: recibir y responder comentarios en un PR | [`s16-evidencia-final.md`](s16-evidencia-final.md) §7 |
| OTR-02 | Ficha S17 | Formulario «Recomendaciones del jurado» | **No clasificable** | El formulario no está disponible; sin la lista no se puede comprobar completitud. Se declara en §0 y se sustituye por las 30 recomendaciones documentables | Este documento §0 |

## 4. Cambios de código y pruebas

Cada cambio aceptado de esta entrega y la prueba que lo respalda. Los cambios sin prueba automatizada
se marcan como tales: no se atribuye cobertura que no existe.

| Cambio | Archivo | Prueba / verificación |
|---|---|---|
| El fallo de persistencia en búsqueda pasa de 500 genérico a **503 controlado** | [`app/busqueda/router.py`](../../app/busqueda/router.py) | `test_si_firestore_no_responde_la_busqueda_devuelve_503` en [`test_resiliencia.py`](../../tests/test_resiliencia.py) |
| El banco de medición solo acepta URL http/https y salida confinada a `docs/evidencia/mediciones` | [`bench_busqueda.py`](../../scripts/medicion/bench_busqueda.py) | 7 casos de ruta rechazada + 4 de URL en [`test_bench_busqueda.py`](../../tests/test_bench_busqueda.py) |
| El reintento del frontend deja de ser un bucle y pasa a recursión con el mismo límite | [`app/frontend/lib/api.ts`](../../app/frontend/lib/api.ts) | Sin runner de frontend; revisión estática y `next build` en CI |
| Accesibilidad del sitio legado: `aria-label` en inputs, `<output>` en estados, `display:block` | [`shareuwensite-main/cuenta.html`](../../shareuwensite-main/cuenta.html), [`panel.html`](../../shareuwensite-main/panel.html), [`index.html`](../../shareuwensite-main/index.html) | Sin navegador automatizado; revisión estática |
| Ternarios anidados y `if` sin llaves resueltos; exports mutables a `const`; *ping* de módulos en paralelo | [`firebase-service.js`](../../shareuwensite-main/firebase-service.js), [`panel.html`](../../shareuwensite-main/panel.html), [`script.js`](../../shareuwensite-main/script.js) | Sin navegador automatizado; revisión estática |
| Validación automática de documentación (rutas, ADR, 417 enlaces, 8 columnas, plantillas) | [`scripts/validar_docs.py`](../../scripts/validar_docs.py) | [`tests/test_docs.py`](../../tests/test_docs.py) y paso «Validar documentación» del workflow |
| C4 nivel 3 del contenedor API | [`c4/nivel3.mmd`](../c4/nivel3.mmd), [`nivel-3.md`](../c4/nivel-3.md) | El validador exige ambos archivos |
| OpenAPI 1.3.1 con la respuesta 503 de búsqueda y el estado real del servidor | [`openapi.yaml`](../api/openapi.yaml) | [`test_contrato.py`](../../tests/test_contrato.py) |
| Workflow: banderas de instalación seguras, `env.SONAR_TOKEN` y validador documental | [`.github/workflows/tests.yml`](../../.github/workflows/tests.yml) | Run de CI tras el push (§7) |

## 5. ADR nuevos, actualizados o reemplazados

No se reescribe ningún ADR aceptado: se añade el puntero de reemplazo que exige la ficha y se
conserva el texto original como decisión histórica.

| ADR | Estado | Qué cambió | Enlace |
|---|---|---|---|
| 0002 · Búsqueda en una sola solicitud | Aceptado | Se añade que su métrica «≤ 3 interacciones» queda **reemplazada por el ADR 0016**; la decisión funcional no cambia | [0002](../adr/0002-usabilidad-busqueda-en-una-solicitud.md) → [0016](../adr/0016-medicion-de-latencia-y-costo-de-lecturas.md) |
| 0006 · Plataforma backend | Aceptado | Apunta a que su parte de persistencia (SQLite sin disco) queda reemplazada por el ADR 0012 | [0006](../adr/0006-plataforma-backend-despliegue.md) → [0012](../adr/0012-persistencia-en-firestore.md) |
| 0012 · Persistencia en Firestore | Aceptado | Declara que reemplaza la persistencia del 0006; corrige la identidad de datos del 0011 | [0012](../adr/0012-persistencia-en-firestore.md) |
| 0016 · Medición de latencia y lecturas | Aceptado | Reemplaza el indicador de interacciones como métrica del sistema | [0016](../adr/0016-medicion-de-latencia-y-costo-de-lecturas.md) |
| 0011, 0015 | Aceptados | Correcciones de contenido ya incorporadas (identidad y garantías); sin cambio de decisión | [0011](../adr/0011-identidad-de-datos-y-propiedad-por-modulo.md), [0015](../adr/0015-mensajeria-asincrona-con-outbox.md) |

**ADR nuevos en esta entrega:** ninguno. La ficha pide ADR nuevos *o* marcados como reemplazados; se
cumple la segunda vía y se dice explícitamente que no se inventó una decisión nueva para llenar el
requisito.

## 6. Diagramas y arc42 coherentes con el código

| Documento | Cambio | Por qué |
|---|---|---|
| [`arc42/05`](../arc42/05-vista-de-bloques-de-construccion.md) | Añade el enlace al C4 nivel 3 y el borde `administracion → documentos` | El nivel 3 descompone el API real; el servicio de administración consulta estadísticas de caché |
| [`arc42/10`](../arc42/10-requisitos-de-calidad.md) | Declara la medición local como límite y enlaza el estado del despliegue | La corrida `--url` sigue pendiente por configuración |
| [`arc42/11`](../arc42/11-riesgos-y-deuda-tecnica.md) | H10/H11/H12 actualizados: 33 incidencias, 503 corregido, dominios activos y búsqueda declarada | Refleja el estado real, no el deseado |
| [`arc42/12`](../arc42/12-glosario.md) | Agrega «Quality Gate», «request-id» y «sitio legado» | Términos usados por la evidencia S16/S17 |
| [`c4/nivel-2.md`](../c4/nivel-2.md) y [`nivel2.mmd`](../c4/nivel2.mmd) | Enlazan el nivel 3 y la dependencia de estadísticas de caché | Coherencia con los componentes implementados |
| [`c4/nivel-3.md`](../c4/nivel-3.md) y [`nivel3.mmd`](../c4/nivel3.mmd) | **Nuevos**: routers, servicios, repositorio, caché, outbox, seguridad y bandeja | Cierra la issue #15 y el eslabón C4 que faltaba |
| [`aspectos.md`](../aspectos.md) | A5, A7 y A3 citan las pruebas y el validador nuevos | La evidencia tiene que existir en la tabla contractual |
| [`README.md`](../../README.md) | Estado del despliegue y del gate actualizados; índice de documentos | Deja de repetir el 404 del 2026-11-16 |

## 7. Ausencia de regresiones

### 7.1 Verificación local (ejecutada)

```text
$ .venv312\Scripts\python.exe -m pytest -q
87 passed, 1 warning

$ .venv312\Scripts\python.exe scripts/validar_docs.py --verbose
Enlaces locales revisados: 417
Filas de aspectos revisadas: 10
ADRs revisados: 16
Validación de documentación: OK (417 enlaces, 10 filas de aspectos, 16 ADR).
```

La prueba de regresión del cambio de comportamiento es explícita: antes del arreglo, el router
dejaba escapar `ErrorPersistencia` y el cliente recibía 500; ahora el test fuerza la excepción y
exige 503. La suite completa sigue en verde, incluidas las pruebas de contrato, fronteras, caché,
idempotencia, eventos y seguridad.

### 7.2 Pipeline remoto (pendiente de push)

El criterio «pipeline en verde **posterior** al último cambio» **no se puede cumplir todavía** desde
el repositorio: los cambios de esta entrega están en el árbol de trabajo y el usuario no ha
autorizado el push. El último run verde es anterior a ellos:

| Run | Fecha | Commit | Estado |
|---|---|---|---|
| [`44001934319`](https://github.com/ISCOUTB/AS_202620_ShareU/actions/runs/44001934319) | 2026-11-17T02:17:57Z | `e129842` | `success` |

Al autorizar el push, el paso «Validar documentación» y la suite completa corren sobre el commit de
cierre. La URL del run y el hash se escriben en esta tabla antes de subir la entrega a Moodle; un run
anterior al cambio no se presenta como prueba.

## 8. Retrospectiva

### 8.1 Qué funcionó

- **Convertir la revisión en artefactos verificables.** Cada hallazgo terminó en un archivo, una
  prueba o una fila de la matriz, no en una respuesta en prosa.
- **Validar la documentación como código.** El validador detectó enlaces y filas de aspectos que una
  lectura humana ya no revisaba; ahora el pipeline los bloquea.
- **Declarar el estado real.** El 500 del despliegue y el gate en ERROR se detectaron al comprobar,
  no al redactar, y se publicaron con `X-Request-Id`, dueño y condición de cierre.

### 8.2 Qué no funcionó

- **El push llegó tarde.** Las correcciones de Sonar y del workflow existían en local mientras el
  remoto seguía mostrando 33 incidencias y un run anterior.
- **La revisión cruzada no ocurrió.** No hay comentarios de otros equipos en los PR; el proceso
  dependía de una coordinación que nadie empujó.
- **La configuración del despliegue quedó incompleta.** El frontend y la API responden, pero sin
  credenciales de Firestore el flujo principal no se puede demostrar en vivo.

### 8.3 Una lección por integrante

| Integrante | Lección específica del proyecto |
|---|---|
| **Dayana Narváez** (arquitectura, ADR, despliegue) | Una tabla de despliegue sin hora, código HTTP y `X-Request-Id` es una promesa, no evidencia. La comprobación del 2026-11-21 cambió la conclusión: el sistema estaba activo y la búsqueda no; declararlo antes de la sustentación fue más útil que maquillarlo |
| **Luis Carlos Corredor** (backend, contrato) | Las pruebas de servicio no cubren el contrato HTTP: `ErrorPersistencia` estaba bien probado en el repositorio y aun así el cliente recibía 500. El borde que traduce excepciones a códigos también necesita prueba |
| **Nicolás Hernández** (caché, eventos) | Un outbox y una caché en memoria son correctos para una instancia, pero el límite hay que probarlo y declararlo: el *stampede* de caché fría (21/300) y la pérdida de eventos al reiniciar son parte del diseño, no notas al pie |
| **Steven Contreras** (documentación, arc42) | Separar arc42 en secciones sirvió, pero la documentación se erosiona en silencio: 417 enlaces y 10 filas de aspectos solo se mantuvieron coherentes cuando un script las revisó en cada push |

### 8.4 Qué harían distinto

1. Empujar cada corrección el mismo día y mirar el run, en vez de acumular deuda local.
2. Habilitar SonarCloud y el validador documental desde la primera semana, no en el cierre.
3. Configurar las credenciales del despliegue antes de la sustentación, para que la demostración en
   vivo no dependiera de una variable de entorno ausente.
4. Pedir la revisión cruzada por nombre y con fecha, no confiar en que ocurra.

## 9. Matriz de cumplimiento S17

| Criterio de la ficha | Evidencia | Estado | Observación |
|---|---|---|---|
| Trabajo posterior al proyecto final | Cambios listados en §4 sobre `e129842` | **Parcial** | Están en el árbol; faltan el commit y el push |
| Matriz con todas las recomendaciones y su origen | §1–§3, 30 filas con origen | **Parcial** | El formulario del jurado no está disponible; se declara |
| Cada recomendación clasificada | Columna «Clasificación» completa (25 A / 3 AP / 2 R) | **Cumple** | `OTR-02` no es clasificable por falta del insumo |
| Motivo técnico de rechazos y aplazamientos | `DOC-11`, `DOC-16`, `DOC-17`, `PAR-12`, `OTR-01` | **Cumple** | Sin «falta de tiempo» a secas |
| Cambios aceptados con enlace a commit o PR | §4 y columna final de §1–§2 | **Parcial** | Los cambios previos tienen PR/commit; los de cierre esperan el hash |
| Pruebas modificadas donde cambió el comportamiento | §4, `test_si_firestore_no_responde_la_busqueda_devuelve_503` | **Cumple con límite** | El frontend y el sitio legado no tienen runner; se declara |
| ADR nuevos o marcados como reemplazados | §5: 0002→0016 y 0006→0012 | **Cumple** | No se reescribió ningún ADR aceptado |
| Diagramas y arc42 coherentes | §6 | **Cumple** | C4 nivel 3 nuevo y secciones actualizadas |
| Pipeline en verde posterior al último cambio | §7.1 local; §7.2 remoto pendiente | **No cumple todavía** | Requiere push y run; no se sustituye por el run de `e129842` |
| Retrospectiva con una lección por integrante | §8.3: 4 lecciones para 4 integrantes | **Cumple** | Lecciones específicas del proyecto |

## 10. Lo que no se afirma

- No se afirma que el formulario del jurado esté cubierto: no se dispone de él.
- No se afirma un pipeline verde sobre el commit de cierre: aún no existe el run.
- No se afirma que el Quality Gate esté en verde: sigue en **ERROR** hasta el reanálisis.
- No se afirma que la búsqueda desplegada funcione: responde 500 por configuración.
- No se afirma revisión cruzada: hay 0 comentarios de *review* en los PR.
