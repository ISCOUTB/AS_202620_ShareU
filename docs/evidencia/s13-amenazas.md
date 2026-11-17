# S13 — Amenazas, dependencias y endurecimiento

## 1. Qué se entregó

- Modelo STRIDE anclado al C4 real, con probabilidad × impacto, dueño y estado:
  [`../seguridad/amenazas.md`](../seguridad/amenazas.md).
- Política de dependencias, auditoría y decisiones sobre hallazgos:
  [`../seguridad/dependencias.md`](../seguridad/dependencias.md).
- Endurecimiento HTTP y credencial administrativa:
  [ADR 0014](../adr/0014-endurecimiento-http-y-escritura-autenticada.md).
- Cambio de contrato: `GET /administracion/revision` exige token (OpenAPI **1.3.0**).

## 2. Amenazas prioritarias y qué se hizo

| Amenaza | Prioridad | Acción | Estado |
|---|---:|---|---|
| Suplantar al administrador (T1) | 12 | `X-Admin-Token` con comparación en tiempo constante; fail-closed | Mitigado parcialmente (token compartido) |
| Leer la bandeja sin credencial (T6) | 12 | Token obligatorio en la bandeja; OpenAPI 1.3.0 | **Mitigado con prueba** |
| Fuga de secretos (T7) | 10 | `.env` fuera de git; barrido `git grep`; logs sin cabeceras ni cuerpos | Mitigado con revisión manual |
| Saturar la API pública (T9) | 9 | Caché + límites de contenedor; sin rate limit | Aceptado con límite |
| Inyección de contenido (T4) | 9 | Validación Pydantic y escape de React; moderación posterior | Aceptado con moderación pendiente |

El resto de la tabla (T2, T3, T5, T8, T10–T15) está en el documento con su decisión. Ninguna amenaza
se marca como «resuelta» sin una prueba o una medida concreta.

## 3. Pruebas de seguridad

```bash
pytest tests/test_seguridad.py tests/test_eventos.py::test_la_bandeja_de_revision_sin_token_es_rechazada -q
```

Cubren: cabeceras de endurecimiento, HSTS solo detrás de HTTPS, CORS con origen permitido y
rechazado, CSP distinta para la documentación, `X-Request-ID` expuesto y bandeja sin token
rechazada. La escritura sin token configurado devuelve 503 y con token incorrecto 401
(`tests/test_idempotencia.py`). El banco de medición valida URL y rutas de salida
(`tests/test_bench_busqueda.py`): solo HTTP/HTTPS, hosts locales salvo permiso explícito y artefactos
dentro de `docs/evidencia/mediciones/`.

## 4. Dependencias

| Control | Resultado |
|---|---|
| `pip-audit -r requirements.in` | `No known vulnerabilities found` (local, 2026-11-16) |
| `npm audit` | Se ejecuta en CI y publica `npm-audit.json`; no bloquea (no hay Node local) |
| Dependabot | PR semanales para pip, npm y Actions |
| `next` | Subido de 14.2.15 (deprecado por seguridad) a **14.2.35** |
| SonarCloud | Gate en **ERROR** al 2026-11-17; hallazgos clasificados en `dependencias.md` D6–D9. Varios corregidos en el repositorio (Dockerfiles, `Annotated`, banco de medición) y pendientes de push |

`pip-audit -r requirements.txt` no se usa porque el archivo tiene hashes y dependencias transitivas
sin pin explícito; la justificación está en [`../seguridad/dependencias.md`](../seguridad/dependencias.md).

## 5. Privacidad

Solo se guarda el nombre del autor. No se registran cuerpos, tokens ni IPs. La bandeja, que muestra
nombres y material pendiente, exige token. La política de retención automática queda declarada como
pendiente antes de operar con datos reales. Ver §4 de [`../seguridad/amenazas.md`](../seguridad/amenazas.md).

## 6. Límite de esta evidencia

El modelo de amenazas es un ejercicio de diseño, no una auditoría externa. No se hizo pentesting ni
prueba de carga hostil. El token compartido no sustituye autenticación de usuarios; se acepta como
medida transitoria y se reabre cuando `usuarios` entre en alcance.

## 7. Trazabilidad

`docs/aspectos.md` (A5, A9) → ADR 0014 → `app/seguridad/autenticacion.py`, `app/main.py`,
`app/administracion/router.py` → `tests/test_seguridad.py`, `tests/test_eventos.py` →
`docs/seguridad/*` → este documento → arc42 §8.6, §11.
