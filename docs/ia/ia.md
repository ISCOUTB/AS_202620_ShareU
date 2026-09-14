# Uso de Inteligencia Artificial

## Propósito

Este archivo registra de manera transparente el uso de herramientas de
inteligencia artificial durante el desarrollo de ShareU, indicando la tarea,
el alcance y la revisión humana aplicada.

## Herramientas

- **Claude (Anthropic):** apoyo en redacción y estructuración de documentación.
- **Asistentes de IA:** apoyo para revisar alternativas, proponer estructuras de
  código y detectar inconsistencias.

La IA no sustituye la decisión del equipo: las decisiones arquitectónicas,
código incorporado y documentación final deben ser revisados por los
integrantes.

## Registro de uso

| Semana | Tarea | Uso de IA | Qué se rechazó y por qué | Resultado / evidencia | Revisión humana | Estado |
|---|---|---|---|---|---|---|
| 3 | Comparación arquitectónica | Apoyo para comparar N-tier, hexagonal y monolito modular frente al escenario de usabilidad | Se descartó adoptar hexagonal en esta fase por su mayor indirección y curva de aprendizaje | Matriz en `docs/aspectos/aspectos.md` y ADR 0001 | Revisión de criterios, costos y consecuencias | Revisado |
| 3 | Esqueleto ejecutable | Propuesta de estructura FastAPI, routers y prueba de arranque | No se incorporó lógica de negocio en la etapa de esqueleto porque correspondía al corte vertical siguiente | `app/main.py` y `tests/test_esqueleto.py` | Ejecución local de las pruebas y revisión de estructura | Revisado |
| 4 | Corte vertical de búsqueda | Apoyo para estructurar servicio, persistencia SQLite, filtros y pruebas | Se evitó introducir un ORM o infraestructura externa para mantener el corte pequeño y reproducible | `app/busqueda/`, `app/documentos/`, `tests/test_busqueda.py` | Revisión del flujo y ejecución de `pytest` | Revisado |
| 4 | Corrección de usabilidad | Apoyo para revisar el flujo de filtros, centralizar el envío y documentar una métrica técnica | No se aceptó presentar la métrica HTTP como si fuera una prueba con usuarios reales | `app/frontend/`, ADR 0002 y `docs/evidencia/medicion-usabilidad.md` | Verificación del contrato frontend/backend y pruebas automatizadas | Revisado |
| 4 | CI | Apoyo para estructurar el workflow de GitHub Actions | No se incluyeron pasos de despliegue porque el objetivo es validar las pruebas | `.github/workflows/tests.yml` | Verificación del workflow y de `pytest` | Revisado |
| 5 | Corrección de issues de SonarCloud | Apoyo para diagnosticar y corregir los 9 issues abiertos (reliability, maintainability, security) detectados por el análisis estático: falta de compare function en `.sort()`, inputs sin label accesible, complejidad cognitiva excedida en `buscar_documentos`, literales duplicados en los datos semilla y dependencias sin versión fija | No se aceptó anclar dependencias mediante hash-locking completo (`--require-hashes`) en esta iteración, por mantener el alcance del corte; se optó por fijar versiones exactas en `requirements.txt` como medida suficiente. **Nota:** esta decisión se revisó después de que SonarCloud marcó `githubactions:S8544`; ver entrada siguiente. | `app/frontend/script.js`, `app/frontend/index.html`, `app/busqueda/service.py`, `app/documentos/repository.py`, `requirements.txt`    ; ver badge en README.md y dashboard en https://sonarcloud.io/project/overview?id=ISCOUTB_AS_202620_ShareU | Verificación de que `tests/test_busqueda.py` siguiera pasando tras el refactor y confirmación de Quality Gate en A en SonarCloud | Revisado |
| 6 | Reconsideración de hash-locking en dependencias | Apoyo para diagnosticar el hallazgo de SonarCloud `githubactions:S8544` ("Using dependencies without locking resolved versions is security-sensitive") sobre `.github/workflows/tests.yml` línea 17, y para generar el `requirements.txt` con hashes reales usando `pip-tools` | Se descartó la opción de simplemente quitar `--require-hashes` del workflow para "apagar" el hotspot, porque eso reabre el riesgo de seguridad que la regla señala; se optó por generar los hashes correctamente en vez de eliminar el control | `requirements.in` (nuevo), `requirements.txt` (regenerado con hashes), `.github/workflows/tests.yml` | Verificación local de `python -m pip install --require-hashes -r requirements.txt` seguido de `pytest -q` en verde, y confirmación de que el hotspot S8544 se resuelve en SonarCloud | Revisado |
| 6 | Contextos delimitados y propiedad de datos | Apoyo para revisar el código actual (imports entre módulos, columnas de la tabla `documentos`) y contrastarlo contra el lenguaje de dominio de `docs/aspectos/aspectos.md` y `docs/arc42/arc42.md`, para identificar contextos, armar la tabla módulo→dato→dueño y redactar el plan de corrección | No se aceptó tratar la ambigüedad de "calificación" como un simple ajuste de nombre; se documentó como una violación de límites de contexto (V1) porque el módulo `calificaciones` no existe todavía y el dato vive en `documentos` con otro significado. Tampoco se aceptó implementar el cambio de una vez: se dejó como ADR propuesto, pendiente de ejecutar | `docs/ddd/contextos.md`, `docs/ddd/propiedad-datos.md`, `docs/ddd/auditoria-violaciones.md`, `docs/adr/0003-separacion-contexto-calificaciones.md` | Verificación manual de los imports reales del repositorio (`grep` sobre `app/`) antes de afirmar cuáles módulos cruzan fronteras; el equipo debe revisar y decidir si se aprueba el ADR 0003 antes de marcarlo como Aceptado | Pendiente de revisión |

## Criterio de rechazo

Cuando una propuesta de IA no coincide con los requisitos de la asignatura,
la arquitectura acordada o el alcance del corte, se descarta y se documenta el
motivo en esta tabla.

## Responsabilidad

El equipo mantiene la responsabilidad sobre las decisiones y el contenido
final del repositorio. La IA se considera una herramienta de apoyo, no una
fuente de autoridad arquitectónica.
