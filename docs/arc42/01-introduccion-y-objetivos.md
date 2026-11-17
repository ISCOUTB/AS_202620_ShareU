# 1. Introducción y objetivos

## 1.1 Descripción

ShareU es una plataforma web para compartir y encontrar material académico
organizado por universidad, carrera y materia. Busca reducir el tiempo que los
estudiantes emplean buscando apuntes, ejercicios, talleres, parciales y otros
recursos dispersos en distintos medios.

## 1.2 Objetivos de calidad

| Objetivo | Prioridad | Indicador |
|---|---|---|
| Usabilidad | Muy alta | Encontrar material relevante en menos de 3 interacciones |
| Seguridad | Alta | Acceso controlado según rol |
| Rendimiento | Alta | Búsquedas con filtros respondidas sin pasos innecesarios |
| Disponibilidad | Alta | API operativa y verificable mediante `/health` |
| Mantenibilidad | Media | Cambios localizados dentro de módulos |
| Escalabilidad | Media | Posibilidad de extraer un módulo si la evidencia lo justifica |

El escenario de usabilidad completo está en
[`../aspectos/aspectos.md`](../aspectos/aspectos.md).
