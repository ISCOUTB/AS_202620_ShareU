# Entrega S13 — resumen de una página

**Tema:** modelado de amenazas y dependencias.

**Método.** STRIDE sobre el C4 real (navegador → Next.js → FastAPI → Firestore, más outbox y token
administrativo). Cada amenaza tiene probabilidad × impacto (1–25), mitigación, riesgo residual,
dueño y estado. Prioridad ≥ 12 exige mitigación o aceptación explícita.

**Prioritarias.**

| Amenaza | Prioridad | Acción | Estado |
|---|---:|---|---|
| Suplantar al administrador | 12 | `X-Admin-Token`, comparación en tiempo constante, fail-closed | Mitigado parcialmente (token compartido) |
| Leer la bandeja sin credencial | 12 | Token obligatorio; OpenAPI 1.3.0 | Mitigado con prueba |
| Fuga de secretos | 10 | `.env` fuera de git, barrido, logs sin cuerpos ni cabeceras | Mitigado con revisión |
| Saturar la API | 9 | Caché y límites de contenedor; sin rate limit | Aceptado con límite |

**Dependencias.** `pip-audit -r requirements.in` sin vulnerabilidades conocidas; `npm audit` en CI
como artefacto; Dependabot semanal; `next` corregido de 14.2.15 a **14.2.35**. Se explica por qué se
audita `requirements.in` y no `requirements.txt` (hashes y transitivas sin pin). El Quality Gate de
SonarCloud está en **ERROR** (44 incidencias) y sus hallazgos se clasifican como deuda aceptada en
`dependencias.md` D6–D9 y arc42 §11.5.

**Privacidad.** Solo nombre del autor; sin cuerpos, tokens ni IPs en logs; bandeja protegida.
Retención automática pendiente antes de datos reales.

**Límite.** Es un ejercicio de diseño, no una auditoría ni un pentesting. El token es transitorio
hasta que exista autenticación de usuarios.

**Enlaces.** [`amenazas.md`](../seguridad/amenazas.md),
[`dependencias.md`](../seguridad/dependencias.md), [`s13-amenazas.md`](../evidencia/s13-amenazas.md),
ADR 0014.
