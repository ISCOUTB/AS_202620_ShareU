# ShareU — guía del proyecto final (tres páginas)

**Entrega:** S16 · proyecto final · `arqsw:final`
**Repositorio:** <https://github.com/ISCOUTB/AS_202620_ShareU>
**Sistema desplegado:** <https://shareu.iscoutb.dev> · API <https://api-shareu.iscoutb.dev>
**Estado del repositorio:** rama `master`, commit `e129842` del 2026-11-16, más los cambios de
cierre que se indican en la matriz S17.
**Verificación del sistema:** 2026-11-21T22:19:51Z (ver página 2).

---

## Página 1 · Qué es ShareU y cómo se ejecuta

ShareU es una plataforma web para **compartir y encontrar material académico** de estudiantes
universitarios: apuntes, talleres, parciales, ejercicios y guías, organizados por universidad,
carrera y materia. El escenario prioritario es que un estudiante encuentre un documento concreto
combinando criterios en **una sola solicitud**, sin recorrer pantallas ni aplicar filtros por
separado.

### Arquitectura en una vista

```text
Navegador -> Next.js 14 (web) -> FastAPI (api) -> Firestore
                                      |
                                      +-> caché de lectura (TTL + invalidación)
                                      +-> outbox en proceso -> bandeja de revisión
```

- **Monolito modular** (ADR 0001): `usuarios`, `documentos`, `busqueda`, `calificaciones` y
  `administracion`. Un módulo solo importa el `service.py` de otro; `tests/test_fronteras.py` lo
  verifica.
- **Persistencia:** Firestore (ADR 0012). La publicación reserva el id con `create()` atómico y es
  idempotente por `Idempotency-Key` + hash SHA-256 del cuerpo.
- **Caché:** lista pública en memoria, TTL de 60 s e invalidación tras escribir (ADR 0013).
- **Mensajería:** outbox en proceso para `documento.publicado`, entrega al menos una vez,
  deduplicación por `event_id`, tres intentos y DLQ (ADR 0015).
- **Seguridad:** `X-Admin-Token` fail-closed, CORS explícito y cabeceras CSP/HSTS/nosniff
  (ADR 0014).
- **Costo:** USD 0/mes con plan Spark, una instancia y caché (ADR 0006/0007).

Los diagramas completos están en [`docs/c4/`](../c4/nivel-2.md): contexto (nivel 1), contenedores
(nivel 2) y **componentes del API (nivel 3)**.

### Arranque con un solo comando

```bash
copy .env.example .env      # Windows; en Linux/macOS: cp .env.example .env
docker compose up --build
```

- Frontend local: <http://127.0.0.1:3000>
- API local: <http://127.0.0.1:8000> · salud en `/health` · OpenAPI en `/docs`

Variables que cambian el comportamiento:

| Variable | Si falta |
|---|---|
| `FIREBASE_CREDENTIALS_JSON` | Las rutas de datos responden **503** fail-closed; `/health` sigue en 200 |
| `SHAREU_ADMIN_TOKEN` | Publicar y leer la bandeja responden **503** |
| `SHAREU_FRONTEND_ORIGIN` | Se aceptan los orígenes locales de Next.js |
| `SHAREU_CACHE_TTL_SEGUNDOS` | 60 s; `0` apaga la caché |
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000` |

### Endpoints que se defienden

| Método y ruta | Qué hace | Credencial |
|---|---|---|
| `GET /health` | Estado del servicio | No |
| `GET /busqueda/documentos` | Búsqueda combinada por universidad, carrera, materia, tipo, palabra clave y calificación mínima | No |
| `POST /documentos` | Publica metadatos con `Idempotency-Key` | `X-Admin-Token` |
| `GET /administracion/metricas` | Búsquedas y tasa sin resultados | No |
| `GET /administracion/eventos` | Contadores del outbox | No |
| `GET /administracion/revision` | Bandeja de revisión | `X-Admin-Token` |
| `POST /administracion/revision/{id}/resolver` | Aprueba y retira de la bandeja | `X-Admin-Token` |

---

## Página 2 · Verificación del sistema entregado

### Comprobación viva del 2026-11-21T22:19:51Z

| URL | Resultado | Evidencia |
|---|---|---|
| `https://shareu.iscoutb.dev` | **200** · HTML de Next.js con título «ShareU — material académico compartido» | Renderiza la interfaz; con la API en fallo muestra «0 resultados» |
| `https://api-shareu.iscoutb.dev/health` | **200** · `{"estado":"ok"}` | `X-Request-Id: c06483a8-f901-42fc-9cbf-e7d17baf44a7` |
| `https://api-shareu.iscoutb.dev/busqueda/documentos` | **500** · `{"detail":"Error interno del servidor"}` | `X-Request-Id: 51a879a9-c134-4358-bc48-f8b5b8ad6fde` |
| `https://api-shareu.iscoutb.dev/ruta-inexistente-xyz` | **404** · `{"detail":"Not Found"}` | `X-Request-Id: f464903f-8080-41b5-97fd-53be11cd6fe0` |
| `https://api-shareu.iscoutb.dev/administracion/revision` | **503** · falta `SHAREU_ADMIN_TOKEN` | `X-Request-Id: 2b62efee-bfa6-4458-80fa-82be44132a63` |

**Lectura honesta:** el frontend y el proceso de la API están activos; los cinco `/ping` responden
200. La búsqueda **no** funciona en el despliegue porque la instancia no tiene configurada la
persistencia de Firestore. No se presenta el 500 como un flujo verificado: es una **no conformidad
de configuración del despliegue**, con dueño (equipo) y condición de cierre (cargar
`FIREBASE_CREDENTIALS_JSON` y `SHAREU_ADMIN_TOKEN` en Dokploy). El código ya traduce el fallo de
persistencia a **503** controlado; ese cambio se valida en local y requiere redespliegue.

### Flujos principales, medidos en local

| Flujo | Resultado | Evidencia |
|---|---|---|
| Buscar y filtrar en una solicitud | 200 con `total` y `resultados` ordenados | [`tests/test_busqueda.py`](../../tests/test_busqueda.py) |
| Publicar con idempotencia | 201 la primera vez; 200 con el mismo cuerpo y clave; 409 con otro cuerpo | [`tests/test_idempotencia.py`](../../tests/test_idempotencia.py) |
| Ver la publicación en la búsqueda | La invalidación de caché la hace visible de inmediato | `test_la_publicacion_queda_visible_en_la_busqueda` |
| Revisión por evento | El documento entra a la bandeja una sola vez | [`tests/test_eventos.py`](../../tests/test_eventos.py) |
| Filtros inválidos | 422 de FastAPI/Pydantic | [`tests/test_contrato.py`](../../tests/test_contrato.py) |

### Caminos de error atendidos

| Situación | Respuesta esperada | Prueba |
|---|---|---|
| Firestore no responde o responde tarde | 503 tras 2 s × 3 intentos, sin colgar la solicitud | [`tests/test_resiliencia.py`](../../tests/test_resiliencia.py), [`tests/test_idempotencia.py`](../../tests/test_idempotencia.py) |
| Falta el token administrativo | 503 fail-closed | `test_sin_token_configurado_la_escritura_esta_apagada` |
| Token incorrecto | 401 | `test_token_incorrecto_devuelve_401` |
| Misma clave, cuerpo distinto | 409 | `test_misma_clave_con_otro_cuerpo_devuelve_409` |
| Consumidor del evento falla | Reintentos 1 s y 2 s; luego DLQ | `test_agotar_los_intentos_manda_el_evento_a_fallidos` |
| Evento duplicado | Se descarta; no duplica la bandeja | `test_un_duplicado_no_crea_dos_entradas_de_revision` |

### Medición reproducible frente al umbral

Umbral de arc42 §10: **p95 ≤ 500 ms**, **error < 1 %**, **≤ 0,1 lecturas Firestore/búsqueda** con
caché. La medición usa `scripts/medicion/bench_busqueda.py`, 300 solicitudes, 20 de
calentamiento, concurrencia 10 y entorno ASGI en proceso con Firestore falso.

| Métrica | Sin caché | Con caché | Veredicto |
|---|---:|---:|---|
| p95 | 72,15 ms | **67,54 ms** | Cumple |
| Tasa de error | 0 % | **0 %** | Cumple |
| Lecturas Firestore/búsqueda | 1,00 | **0,07** | Cumple |

Artefactos: [`s10-linea-base-sin-cache.md`](../evidencia/mediciones/s10-linea-base-sin-cache.md) y
[`s14-local-asgi.md`](../evidencia/mediciones/s14-local-asgi.md). **Límite:** el modo ASGI no
incluye red ni Firestore reales; el número es un límite inferior y no se extrapola al despliegue.

---

## Página 3 · Desafío, alcance, decisiones y sustentación

### Respuesta al desafío final

El texto literal asignado por el jurado **no consta en el repositorio ni en la información pública
del curso**; se declara como insumo faltante para no inventar una consigna. La respuesta se
contrasta contra el desafío que el escenario prioritario impone y que la ficha S16 permite
verificar: **sostener la búsqueda y la publicación cuando Firestore falla, responde tarde o la
carga sube, sin salir del costo cero y sin perder consistencia**.

| Riesgo del desafío | Respuesta implementada | Evidencia |
|---|---|---|
| Firestore caído o lento | Timeout 2 s, 3 intentos, 503 controlado; la caché tibia sigue sirviendo | `_con_reintentos`, `test_timeout_se_reporta_como_error_de_persistencia` |
| Reintento del cliente | `Idempotency-Key` + hash; 200/409 sin duplicar | `test_repetir_la_misma_clave_no_duplica` |
| Consumidor caído | Outbox con reintentos y DLQ; la publicación responde igual | `test_agotar_los_intentos_manda_el_evento_a_fallidos` |
| Carga concurrente | Caché con TTL e invalidación; medición reproducible | `s14-local-asgi.md` |
| Cambio de proveedor | Persistencia aislada en `documentos/repository.py`; ADR 0012 y criterio de reapertura | ADR 0012 |

La **cuantificación frente a la línea base** está en la tabla de la página 2: 67,54 ms frente a
72,15 ms y 0,07 lecturas frente a 1,00. No hay una corrida contra el despliegue porque su búsqueda
responde 500 por configuración; se declara en lugar de extrapolar.

### Alcance comprometido frente a entregado

| Comprometido en el segundo corte | Entregado | Estado |
|---|---|---|
| Búsqueda combinada en una solicitud | Implementada y probada | Cumple |
| Publicación idempotente | Implementada con `create()` atómico y hash | Cumple |
| Caché con invalidación | Implementada, medida y observable | Cumple |
| Mensajería con deduplicación y DLQ | Outbox en proceso, contrato y pruebas | Cumple con límite de memoria |
| Seguridad administrativa | `X-Admin-Token` fail-closed y cabeceras | Cumple |
| Despliegue verificado | Frontend y API activos; búsqueda sin persistencia configurada | **Parcial, declarado** |
| Autenticación de estudiantes y archivos | Fuera de alcance desde el inicio | **No comprometido** |

Lo no hecho está declarado en [`docs/arc42/11-riesgos-y-deuda-tecnica.md`](../arc42/11-riesgos-y-deuda-tecnica.md)
§11.2 y en [`README.md`](../../README.md) §Limitaciones. Un alcance recortado y declarado no se
presenta como completo.

### Decisiones que explican la evolución

Los 16 ADR se recorren en orden en [`docs/adr/`](../adr/). La evolución se reconstruye con al menos
una decisión **reemplazada** y otra **confirmada**:

- **Reemplazada:** el ADR 0006 (plataforma backend) aceptaba SQLite sin disco persistente; el
  ADR 0012 reemplaza esa parte con Firestore y deja el enlace al sustituto.
- **Confirmada con evidencia:** el ADR 0010 decidió **no extraer** módulos; la medición de S10/S14
  y el tamaño del sistema confirman que no hay carga que justifique un servicio aparte.
- **Ajustada por medición:** el ADR 0002 usaba «≤ 3 interacciones»; el ADR 0016 lo reemplaza como
  métrica del sistema por p95, error y lecturas, conservando la prueba funcional.

### Documentación, trazabilidad y validación automática

- arc42 completo, secciones 1–12 con glosario: [`docs/arc42/00-portada.md`](../arc42/00-portada.md).
- C4 niveles 1–3: [`docs/c4/nivel-2.md`](../c4/nivel-2.md) y [`docs/c4/nivel-3.md`](../c4/nivel-3.md).
- Tabla de aspectos A1–A10 con ocho columnas navegables: [`docs/aspectos.md`](../aspectos.md).
- Contrato OpenAPI 1.3.1: [`docs/api/openapi.yaml`](../api/openapi.yaml).
- **Validación automática:** `python scripts/validar_docs.py` comprueba rutas obligatorias,
  nombres de ADR, **417 enlaces locales**, las 10 filas de aspectos y ausencia de marcadores de
  plantilla. El paso «Validar documentación» del workflow lo ejecuta en cada push, y
  `tests/test_docs.py` lo integra en `pytest`.

### Contribuciones verificables

| Integrante | Cuenta(s) | Commits | Aporte principal |
|---|---|---:|---|
| Dayana Narváez | `daynarvaez` | 28 | Arquitectura, documentación, ADR, despliegue y cierre |
| Luis Carlos Corredor | `luiscorredor` | 15 | Backend, pruebas y contrato |
| Nicolas Hernández | `Nicolas-HH` | 14 | Backend, caché, eventos y pruebas |
| Steven Contreras | `stevencontre` (+ `SaintChoppa`, 1 commit/PR) | 5 (+1) | Documentación y separación de arc42 |

`git shortlog -sne HEAD` y la actividad por mes están en la evidencia S16. **Límite declarado:** no
hay comentarios de revisión cruzada en los PR del repositorio (0 comentarios en la API de GitHub);
es una no conformidad de proceso, no se presenta como cumplida.

### Tres preguntas contrafactuales para el jurado

1. **Si la carga se multiplica por diez**, ¿qué se rompe primero: la caché, Firestore o el proceso
   único? La respuesta esperada es el límite de una instancia y el *stampede* de caché fría; el
   criterio de reapertura está en los ADR 0013/0015.
2. **Si Firestore cae durante una publicación**, ¿se pierde el documento o el evento? El documento
   no se crea (503); si ya se creó y el consumidor falla, el evento queda en el outbox y se
   reintenta, con DLQ tras tres intentos y pérdida declarada al reiniciar.
3. **Si se cambia de proveedor de datos**, ¿qué parte del sistema se reescribe? Solo
   `documentos/repository.py` y su credencial; búsqueda, administración y frontend hablan con
   interfaces. El costo y el esfuerzo se comparan en el ADR 0012.

### Cierre honesto

El sistema demuestra en local el escenario prioritario, la idempotencia, la resiliencia y la
seguridad administrativa. El despliegue está activo pero **no completa el flujo de datos** por
configuración de Firestore; el Quality Gate de SonarCloud sigue en **ERROR** hasta que se empujen
las correcciones de esta entrega y se reanalice. Ninguna de las dos cosas se oculta: se declaran con
su evidencia, su dueño y su condición de cierre.
