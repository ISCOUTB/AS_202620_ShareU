# Evidencia S9 — Generación verificada y trazable

- **Commit base auditado:** `c552056` (2026-09-28). Completar con el hash del commit final al subir.
- **Porción construida con IA:** métrica de búsquedas sin resultados (semana 8, fila 8 de `docs/ia/ia.md`).
  Código: `app/administracion/metricas.py`, `app/administracion/router.py`, `app/busqueda/service.py`.
  Commit de origen: `332f67f`.

## 1. Cadena del aspecto

| Eslabón | Destino |
|---|---|
| Aspecto | Usabilidad, `docs/aspectos/aspectos.md` (fila nueva de S9 en la tabla de trazabilidad) |
| Decisión del equipo | [ADR 0008](../adr/0008-metrica-tras-interfaz-de-administracion.md) (alternativas A a D argumentadas con costo USD 0, sin disco persistente y ADR 0001) |
| Código | `app/administracion/service.py`, `app/busqueda/service.py` |
| Pruebas | `tests/test_metricas.py`, `tests/test_fronteras.py`, `tests/test_escenario_usabilidad.py` |
| Medición | sección 3 |

## 2. Pruebas que fallan ante el defecto que cubren

Cada defecto se introdujo a propósito y luego se revirtió (`git checkout`).

| Defecto introducido | Prueba que falla |
|---|---|
| `busqueda/service.py` vuelve a importar `app.administracion.metricas` | `test_fronteras.py::test_modulos_solo_se_hablan_por_service` (`AssertionError: ['busqueda/se…ion.metricas'] == []`) |
| `metricas.py`: `if total_resultados == 0` cambiado a `!= 0` | `test_metricas.py`: 2 fallos (`test_busqueda_con_resultados_no_cuenta_como_sin_resultados` y `test_busqueda_sin_resultados_se_cuenta`) |
| Datos de ejemplo con materia y tipo repetidos | `test_escenario_usabilidad.py`: `assert 6 <= 3` |

Estado final: `pytest -q` → 12 passed.

## 3. Medición del escenario

Interacciones = campos llenados + 1 clic en «Buscar». Umbral: <= 3.

| Documento | Interacciones mínimas |
|---|---|
| Taller de Python | 2 |
| Parcial de Bases de Datos | 2 |
| Apuntes de Arquitectura de Software | 2 |
| Ejercicios de Cálculo | 2 |
| Guía de Redes | 2 |

Resultado: máximo 2 <= 3. Es un indicador técnico sobre los datos de ejemplo, no una
prueba con estudiantes (ver `medicion-usabilidad.md`).

## 4. Extracto de `docs/ia/ia.md`

Fila 9 (aceptado / corregido / rechazado con motivo) y fila 8 con el marcador resuelto.
Salida rechazada principal: dejar el import cruzado y solo actualizar la documentación.

## 5. Auditoría de erosión

Barrido de la ficha: `git grep -nIE '(INSERT INTO|UPDATE |\.save\(|\.create\(|repository\.)' HEAD -- . ':!docs'`
→ solo `documentos/repository.py` (dueño de su tabla). Ningún módulo escribe tablas ajenas.
Barrido de imports: `git grep -nE '^from app\.' HEAD -- app`.

| # | Hallazgo | Ubicación | Corrección |
|---|---|---|---|
| E1 | `busqueda` importaba un archivo interno de `administracion` | `app/busqueda/service.py` L6 | Fachada `administracion/service.py` + `test_fronteras.py` (ADR 0008) |
| E2 | `propiedad-datos.md` decía que el único cruce era `busqueda -> documentos.service` | `docs/ddd/propiedad-datos.md` | Actualizado |
| E3 | README y arc42 citan archivos que no están en el repositorio: `tests/test_contrato.py`, `Dockerfile`, `render.yaml`, ADR 0005 a 0007 | README, `docs/arc42/arc42.md` §2, §7, §8.5 | **Pendiente:** subir los archivos o quitar la referencia |
| E4 | Marcadores sin resolver en `ia.md` (`<URL Render>`, `<URL Vercel>`, `<integrante>`, `<URL del run en Actions>`) y en README | `docs/ia/ia.md` filas 7 y 8, README | **Pendiente:** completar |

## 6. Dependencias propuestas por el modelo

Desde `0c2b53a` se añadieron `pyyaml==6.0.2` y `jsonschema==4.23.0`, más el starter de Next.js.

- Las 26 entradas de `requirements.txt` existen en PyPI con esa versión (respuesta 200 en
  `pypi.org/pypi/<paquete>/<versión>/json`) y `pip install --require-hashes` en entorno limpio
  termina sin errores; PyYAML y jsonschema apuntan a sus repositorios oficiales.
- Los 7 paquetes directos de `app/frontend/package.json` existen en el registro de npm con
  historial desde 2011 a 2016 (no son nombres recientes).
- **Hallazgo:** `next@14.2.15` está marcado como deprecado por vulnerabilidad de seguridad en el registro.
  La última 14.2.x sin marca es `14.2.35`. Corrección: `cd app/frontend && npm install next@14.2.35`.

## 7. Credenciales

`git grep -nIiE '(api[_-]?key|secret|passw(or)?d|token|bearer|BEGIN (RSA|OPENSSH|PRIVATE)|AKIA…|sk-…|ghp_…)' HEAD`
(incluye `docs/` y ejemplos): solo referencias a `secrets.GITHUB_TOKEN` y `secrets.SONAR_TOKEN`
en el workflow y una mención en el README. El único `.env` versionado es `app/frontend/.env.example`
y contiene solo una URL local.

## 8. Componente generativo

Decisión de no incorporarlo: [ADR 0009](../adr/0009-no-incorporar-componente-generativo.md).
