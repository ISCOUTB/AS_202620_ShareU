# Evidencia S16 · proyecto final

| | |
|---|---|
| Ficha | `arqsw:final` (semana 16) |
| Repositorio | `ISCOUTB/AS_202620_ShareU`, rama `master` |
| Estado calificado | `e129842` · 2026-11-16T21:17:49-05:00 |
| Cambios de cierre | Los de esta entrega, publicados en el commit de cierre y trazados en la matriz S17 |
| Verificación del sistema | 2026-11-21T22:19:51Z |
| Documento guía | [`final-guia-tres-paginas.md`](final-guia-tres-paginas.md) |

## 1. Estado final y alcance del cambio

El último commit de `master` anterior al cierre es `e129842`. El proyecto cambió desde la línea
base del segundo corte (`39508608`, 2026-09-28): **118 archivos, +8 486 / −1 517 líneas** y 14
commits en la ventana. El cambio incluye Firestore real, caché, outbox, seguridad administrativa,
Docker/Dokploy, medición, arc42 1–12, ADR 0011–0016, C4 1–3 y la tabla de aspectos completa.

```text
git diff --stat 39508608..e129842   -> 118 files changed, 8486 insertions(+), 1517 deletions(-)
git log --format='%h %cI %an %s' 39508608..e129842
```

## 2. Sistema desplegado: comprobación viva

Comando y hora (UTC): `curl` contra cada URL el **2026-11-21T22:19:51Z**.

| Comprobación | Resultado | Evidencia |
|---|---|---|
| `GET https://shareu.iscoutb.dev` | **200** · HTML de Next.js, título «ShareU — material académico compartido» | Interfaz servida; con la API en fallo muestra «0 resultados» |
| `GET https://api-shareu.iscoutb.dev/health` | **200** · `{"estado":"ok"}` | `X-Request-Id: c06483a8-f901-42fc-9cbf-e7d17baf44a7` |
| `GET https://api-shareu.iscoutb.dev/busqueda/documentos` | **500** · `{"detail":"Error interno del servidor"}` | `X-Request-Id: 51a879a9-c134-4358-bc48-f8b5b8ad6fde` |
| `GET https://api-shareu.iscoutb.dev/ruta-inexistente-xyz` | **404** · `{"detail":"Not Found"}` | `X-Request-Id: f464903f-8080-41b5-97fd-53be11cd6fe0` |
| `GET https://api-shareu.iscoutb.dev/administracion/revision` | **503** · falta `SHAREU_ADMIN_TOKEN` | `X-Request-Id: 2b62efee-bfa6-4458-80fa-82be44132a63` |
| `GET` de los cinco `/ping` | **200** | `usuarios`, `documentos`, `busqueda`, `calificaciones`, `administracion` |

**Diagnóstico declarado.** El proceso y el frontend están activos. La búsqueda falla porque la
instancia no tiene configurada la persistencia de Firestore; el contenedor no expone logs al
equipo desde el repositorio, así que la causa se infiere de la configuración y **no se afirma como
verificada**. El código ya convierte `ErrorPersistencia` en **503** controlado
(`app/busqueda/router.py`), pero el cambio necesita redespliegue para observarse. Mientras tanto,
el 500 es una **no conformidad de configuración**, con dueño y condición de cierre.

## 3. Flujos principales y caminos de error

| Flujo / error | Resultado local | Evidencia |
|---|---|---|
| Búsqueda combinada en una solicitud | 200 con `total` y `resultados` ordenados | `tests/test_busqueda.py` |
| Publicación idempotente | 201; 200 con misma clave y cuerpo; 409 con otro cuerpo | `tests/test_idempotencia.py` |
| Publicación visible de inmediato | Invalidación de caché | `test_la_publicacion_queda_visible_en_la_busqueda` |
| Bandeja alimentada por evento | Una entrada por documento | `tests/test_eventos.py` |
| Firestore no responde | 503 tras timeout y reintentos | `tests/test_resiliencia.py`, `test_timeout_se_reporta_como_error_de_persistencia` |
| Sin token administrativo | 503 fail-closed | `test_sin_token_configurado_la_escritura_esta_apagada` |
| Token incorrecto | 401 | `test_token_incorrecto_devuelve_401` |
| Cuerpo inválido | 422 | `tests/test_contrato.py` |
| Ruta inexistente | 404 | comprobación viva de la tabla anterior |

## 4. Respuesta al desafío final

El texto literal del desafío asignado **no consta en el repositorio ni en la información pública
del curso**. Se declara como insumo faltante en lugar de inventar una consigna. La respuesta se
contrasta contra el desafío verificable del escenario prioritario: **sostener búsqueda y
publicación ante fallo, lentitud o carga de Firestore, sin salir del costo cero y sin perder
consistencia**.

| Frente | Implementación | Cuantificación / prueba |
|---|---|---|
| Firestore caído o lento | Timeout 2 s, 3 intentos, 503; caché tibia sigue sirviendo | `_con_reintentos`; pruebas de timeout y reintento |
| Reintento del cliente | `Idempotency-Key` + hash; 200/409 sin duplicar | `test_repetir_la_misma_clave_no_duplica` |
| Consumidor caído | Outbox con reintentos 1 s/2 s y DLQ | `test_agotar_los_intentos_manda_el_evento_a_fallidos` |
| Carga concurrente | Caché TTL + invalidación; medición reproducible | p95 67,54 ms; 0,07 lecturas/búsqueda |
| Cambio de proveedor | Persistencia aislada en `documentos/repository.py` | ADR 0012 y criterio de reapertura |

La comparación con la línea base es explícita: **67,54 ms frente a 72,15 ms** y **0,07 frente a
1,00** lecturas. No hay corrida contra el despliegue porque su búsqueda responde 500; se declara el
límite en lugar de extrapolar.

## 5. Matriz de cumplimiento de la ficha S16

| Criterio | Evidencia | Estado | Observaciones |
|---|---|---|---|
| Estado final identificable y anterior al cierre | `e129842`, 2026-11-16T21:17:49-05:00, rama `master` | Cumple | Hash y fecha citados |
| Sistema desplegado y estable en la revisión | Frontend 200, `/health` 200, cinco `/ping` 200, 404 y 503 correctos | **Parcial** | Búsqueda 500 por configuración de Firestore; declarado |
| Flujos principales con datos realistas | Búsqueda y publicación probadas en local con Firestore falso y semilla | **Parcial** | No verificables en el despliegue por la configuración |
| Caminos de error atendidos | 401, 404, 409, 422, 503 con pruebas | Cumple | Ver §3 |
| Desafío final implementado y evidenciado | Degradación controlada, idempotencia, outbox y medición | **Parcial** | Texto asignado no disponible; se declara |
| Alcance entregado vs. comprometido | Guía de tres páginas §Alcance; deuda en arc42 §11.2 | Cumple | Lo no hecho está declarado |
| ADR que reconstruyen la evolución | 16 ADR en orden; 0006→0012 reemplazo; 0010 confirmado; 0016 ajusta 0002 | Cumple | Enlaces en la guía y en S17 |
| Al menos una decisión confirmada o reemplazada | ADR 0012 reemplaza la persistencia de 0006; ADR 0010 confirmado con medición | Cumple | Enlaces explícitos |
| Atributos medidos y contrastados | p95, error y lecturas con artefactos JSON/Markdown | Cumple | Medición local ASGI, límite declarado |
| Modos de fallo y mitigaciones | Pruebas de timeout, reintento, duplicado y DLQ | Cumple | `pytest` en verde |
| arc42 1–12 con glosario, sin plantilla | Archivos 00–12; validador sin marcadores | Cumple | `scripts/validar_docs.py` |
| C4 niveles 1–3 del sistema entregado | `nivel1.mmd`, `nivel-2.md`, `nivel-3.md` + `.mmd` | Cumple | Nivel 3 descompone el API real |
| Tabla de aspectos recorrible | A1–A10, ocho columnas, 10/10 verificadas | Cumple | Validador exige columnas navegables |
| Validación automática en el pipeline | Paso «Validar documentación» + `tests/test_docs.py` | Cumple | Ejecutado en verde en los runs `44973782961`, `44973929626` y `44974059013` |
| Contribución de todos los integrantes | `shortlog`: Dayana 28, Luis 15, Nicolas 14, Steven 5 (+1) | Cumple con límite | Actividad de octubre baja (1 commit); se declara |
| Revisión cruzada con comentarios de fondo | 0 comentarios de review en la API de GitHub | **No cumple** | No se presenta como cumplido |
| Demostración y sustentación | Sesión ante docente y jurado | No verificado | No verificable desde el repositorio |

## 6. Documentación, C4 y validación automática

- **arc42:** [`00-portada.md`](../arc42/00-portada.md) enlaza las secciones 1–12 y el glosario.
- **C4 nivel 3:** [`nivel-3.md`](../c4/nivel-3.md) y [`nivel3.mmd`](../c4/nivel3.mmd); descompone
  routers, servicios, repositorio, caché, outbox, seguridad y bandeja.
- **Aspectos:** [`docs/aspectos.md`](../aspectos.md), A1–A10.
- **Validador:** `python scripts/validar_docs.py --verbose` →
  `OK (417 enlaces, 10 filas de aspectos, 16 ADR)`. Comprueba rutas obligatorias, convención de
  nombres de ADR, enlaces locales, columnas navegables y ausencia de marcadores de plantilla.
- **Integración:** el workflow ejecuta el validador y `tests/test_docs.py` lo cubre en `pytest`.

## 7. Contribuciones y colaboración

```text
git shortlog -sne HEAD
    15  Dayana <daynarvaez@utb.edu.co>
    15  luiscorredor <corredorluis142@gmail.com>
    14  Nicolas-HH <nichernandez@utb.edu.co>
    13  daynarvaez <daynarvaez@utb.edu.co>
     5  steven <sc478079@gmail.com>
     1  SaintChoppa
```

Agrupado por persona (Dayana suma 28) y contrastado con `EQUIPOS.md`:

| Integrante | Cuenta(s) | Commits | Responsabilidad documentada |
|---|---|---:|---|
| Dayana Narváez | `daynarvaez` | 28 | Arquitectura, ADR, documentación, despliegue, cierre |
| Luis Carlos Corredor | `luiscorredor` | 15 | Backend, contrato y pruebas |
| Nicolas Hernández | `Nicolas-HH` | 14 | Caché, eventos, pruebas |
| Steven Contreras | `stevencontre` / `steven` (+ `SaintChoppa`) | 5 (+1) | Documentación y separación de arc42 |

**Límites declarados:** la actividad por mes es desigual (sep 49, oct 1, nov 12); no hay comentarios
de revisión cruzada en los PR; la cuenta `SaintChoppa` no se puede atribuir con certeza a una
persona desde el repositorio. Se declaran como no conformidades de proceso.

## 8. Preguntas contrafactuales preparadas

1. **Carga ×10:** ¿qué se rompe primero? Una instancia, la caché fría y el *stampede*; el límite y
   la condición de reapertura están en ADR 0013/0015.
2. **Firestore cae en una publicación:** ¿se pierde el documento o el evento? Sin documento no hay
   201; si el consumidor falla, el evento queda en outbox, se reintenta y termina en DLQ tras tres
   intentos; un reinicio pierde pendientes (límite declarado).
3. **Cambio de proveedor de datos:** ¿qué se reescribe? Solo `documentos/repository.py` y la
   credencial; el resto habla con interfaces. El costo se compara en ADR 0012.

## 9. Lo que no se afirma

- No se afirma que la búsqueda desplegada funcione: responde 500 al 2026-11-21.
- No se afirma un Quality Gate en verde por el paso del workflow: ese paso sigue en `skipped` por
  falta de `SONAR_TOKEN`. El gate **sí** está en OK sobre `75bc601` según el análisis automático de
  SonarCloud (0 incidencias), y así se cita con su fuente.
- No se afirma revisión cruzada: hay 0 comentarios de review.
- No se afirma que la medición represente el despliegue: es ASGI en proceso, sin red real.
