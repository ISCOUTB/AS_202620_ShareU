# Uso de Inteligencia Artificial

## Propósito

Este archivo registra de manera transparente el uso de herramientas de
inteligencia artificial durante el desarrollo de ShareU, indicando la tarea,
el alcance y la revisión humana aplicada.

## Herramientas

- **Claude (Anthropic):** apoyo en redacción y estructuración de documentación.
- **Asistentes de IA:** apoyo para revisar alternativas, proponer estructuras
  de código y detectar inconsistencias.

La IA no sustituye la decisión del equipo: las decisiones arquitectónicas,
código incorporado y documentación final deben ser revisados por los
integrantes.

## Registro de uso

| Semana | Tarea | Uso de IA | Qué se rechazó y por qué | Resultado / evidencia | Revisión humana | Estado |
|---|---|---|---|---|---|---|
| 3 | Comparación arquitectónica | Apoyo para comparar N-tier, hexagonal y monolito modular frente al escenario de usabilidad | Se descartó adoptar hexagonal en esta fase por su mayor indirección y curva de aprendizaje | Matriz en `docs/aspectos/aspectos.md` y ADR 0001 | El equipo revisa criterios, costos y consecuencias antes de aceptar el ADR | Revisado |
| 3 | Esqueleto ejecutable | Propuesta de estructura FastAPI, routers y prueba de arranque | No se incorporó lógica de negocio en la etapa de esqueleto porque correspondía al corte vertical siguiente | `app/main.py` y `tests/test_esqueleto.py` | Ejecución local de las pruebas y revisión de estructura | Revisado |
| 4 | Corte vertical de búsqueda | Apoyo para estructurar servicio, persistencia SQLite, filtros y pruebas | Se evitó introducir un ORM o infraestructura externa para mantener el corte pequeño y reproducible | `app/busqueda/`, `app/documentos/`, `tests/test_busqueda.py` | Revisión del flujo Router → Service → Repository y ejecución de `pytest` | Pendiente de validación final del equipo |
| 4 | CI | Apoyo para estructurar el workflow de GitHub Actions | No se incluyeron pasos de despliegue porque el objetivo del corte es evidencia de pruebas | `.github/workflows/tests.yml` | Verificación del workflow y del resultado verde en GitHub | Pendiente de validación final del equipo |

## Criterio de rechazo

Cuando una propuesta de IA no coincide con los requisitos de la asignatura,
la arquitectura acordada o el alcance del corte, se descarta y se documenta el
motivo en esta tabla.

## Responsabilidad

El equipo mantiene la responsabilidad sobre las decisiones y el contenido
final del repositorio. La IA se considera una herramienta de apoyo, no una
fuente de autoridad arquitectónica.
