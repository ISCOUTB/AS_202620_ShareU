# Idea del proyecto

UniShare es una plataforma web pensada para estudiantes universitarios. La idea principal es tener un espacio donde se pueda compartir material académico como apuntes, ejercicios, talleres, parciales y otros documentos relacionados con las materias. De esta manera, un estudiante que necesite material para estudiar puede buscarlo y descargarlo desde la plataforma, mientras que quienes tengan documentos útiles pueden compartirlos con otros estudiantes.

La plataforma permitiría buscar los documentos utilizando diferentes datos, como la universidad, la carrera, la materia, el tipo de documento, una palabra clave y la calificación. Esto haría que encontrar material académico específico sea mucho más sencillo.

## Aspecto declarado: Usabilidad

La usabilidad es un aspecto crítico porque el valor principal de la plataforma depende de que los estudiantes puedan buscar y encontrar material académico de forma ágil; si esto no es sencillo, los usuarios volverán a utilizar métodos informales como WhatsApp, Google Drive o compartir archivos directamente entre compañeros, que es precisamente el problema que el proyecto busca resolver.

### Escenario de calidad

| Elemento                | Descripción                                                                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Fuente del estímulo** | Un estudiante universitario que utiliza la plataforma UniShare                                                                                               |
| **Estímulo**            | El usuario ingresa a la plataforma buscando material académico específico de una materia                                                                     |
| **Artefacto**           | Módulo de búsqueda y filtrado de documentos                                                                                                                  |
| **Entorno**             | Uso normal, desde computador o celular, con o sin experiencia previa en la plataforma                                                                        |
| **Respuesta**           | El sistema permite filtrar resultados por universidad, carrera, materia, tipo de documento y/o palabra clave, mostrando documentos relevantes de forma clara |
| **Medida de respuesta** | El usuario logra encontrar un documento relevante en menos de 3 interacciones (clics/filtros), sin necesidad de ayuda externa o instrucciones adicionales    |

### Decisiones/tácticas para lograrlo

* Interfaz de filtros simple y visible (universidad, carrera, materia, tipo de documento y palabra clave) en la misma vista de resultados, evitando pasos adicionales.
* Uso de componentes de UI estándar y reconocibles (buscador con ícono de lupa, menús desplegables y filtros) para reducir la curva de aprendizaje.
* Resultados de búsqueda con información clave visible de inmediato (título, materia, tipo de documento, autor y calificación) sin tener que abrir cada publicación.
* Diseño responsivo, priorizando el uso desde celular, dado que es uno de los dispositivos más utilizados por los estudiantes.
* Mensajes claros cuando no hay resultados, sugiriendo ajustar los filtros o realizar una nueva búsqueda en lugar de dejar una pantalla vacía sin explicación.

### Forma de verificación

* Pruebas de usabilidad con un grupo reducido de usuarios reales (estudiantes), midiendo tiempo y número de clics para encontrar un documento de prueba.
* Revisión heurística de la interfaz de búsqueda y filtros antes de cada entrega incremental.

