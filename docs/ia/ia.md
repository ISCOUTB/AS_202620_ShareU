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
| 4 | Corrección de issues de SonarCloud | Apoyo para diagnosticar y corregir los 9 issues abiertos (reliability, maintainability, security) detectados por el análisis estático: falta de compare function en `.sort()`, inputs sin label accesible, complejidad cognitiva excedida en `buscar_documentos`, literales duplicados en los datos semilla y dependencias sin versión fija | No se aceptó anclar dependencias mediante hash-locking completo (`--require-hashes`) en esta iteración, por mantener el alcance del corte; se optó por fijar versiones exactas en `requirements.txt` como medida suficiente | `app/frontend/script.js`, `app/frontend/index.html`, `app/busqueda/service.py`, `app/documentos/repository.py`, `requirements.txt` | Verificación de que `tests/test_busqueda.py` siguiera pasando tras el refactor y confirmación de Quality Gate en A en SonarCloud | Revisado |

## Criterio de rechazo

Cuando una propuesta de IA no coincide con los requisitos de la asignatura,
la arquitectura acordada o el alcance del corte, se descarta y se documenta el
motivo en esta tabla.

## Responsabilidad

El equipo mantiene la responsabilidad sobre las decisiones y el contenido
final del repositorio. La IA se considera una herramienta de apoyo, no una
fuente de autoridad arquitectónica.
