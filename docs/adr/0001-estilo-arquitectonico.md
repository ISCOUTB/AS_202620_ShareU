# ADR 0001: Estilo arquitectónico de ShareU


## Contexto
ShareU es una plataforma web para compartir material académico entre estudiantes
universitarios, organizada por universidad, carrera y materia (ver `README.md` y
`docs/arc42-template-EN.md`, sección Introduction and Goals).

El aspecto de calidad declarado como crítico (`docs/aspectos.md`) es la
**usabilidad**: un estudiante debe encontrar un documento relevante en menos de
3 interacciones (clics/filtros) usando el módulo de búsqueda y filtrado, sin
ayuda externa. Le siguen en prioridad seguridad, rendimiento y disponibilidad
(altas), y mantenibilidad y escalabilidad (medias).

El sistema tiene dominios claramente separables: **usuarios**, **documentos**,
**búsqueda/filtrado**, **calificaciones** y **administración** (reportes y
moderación). El equipo es reducido (estudiantes), sin experiencia previa en
despliegue distribuido, y el proyecto se entrega de forma incremental semana a
semana.

## Decisión
Se adopta un **monolito modular**: un único desplegable organizado en módulos
de dominio (usuarios, documentos, búsqueda, calificaciones, administración),
con fronteras explícitas y comunicación controlada entre módulos. Cada módulo
expone su propia interfaz interna y no accede directamente a los datos de otro.

## Alternativas consideradas

### Capas (N-tier) — descartada
Favorece la simplicidad inicial (frontera por capa técnica: presentación,
lógica, datos), pero concentraría la lógica de negocio de dominios que
queremos mantener independientes (búsqueda, calificación, moderación) en las
mismas capas de servicio. Un cambio en las reglas de un dominio arrastraría
cambios transversales en capas compartidas, justo el riesgo que el estilo
introduce según su costo declarado ("cambios transversales").

### Hexagonal (puertos y adaptadores) — descartada por ahora
Ofrece mejor testabilidad y facilidad para sustituir adaptadores (p. ej.,
cambiar el motor de almacenamiento de documentos), pero introduce más
indirección y una curva de aprendizaje que el equipo, sin experiencia previa
con el patrón y con tiempo limitado por semana de entrega, no puede sostener
de forma consistente en las primeras iteraciones. Se reevaluará si aparece
una necesidad concreta de sustituir infraestructura que justifique el costo.

## Consecuencias
- **Se gana:** organización que refleja el modelo real de ShareU, facilitando
  ubicar y modificar funcionalidad de un dominio sin tocar los demás.
- **Se asume:** vigilar el acoplamiento entre módulos es responsabilidad del
  equipo; sin revisión constante en cada entrega, los límites pueden
  erosionarse (riesgo propio de este estilo).
- **Queda abierto:** extraer un módulo (por ejemplo, búsqueda, si el
  rendimiento lo exige) hacia un servicio independiente en una fase
  posterior, sin rediseñar el sistema completo — esto da soporte a la
  escalabilidad como objetivo de calidad de prioridad media.
- **No se obtiene**, en esta fase, el nivel de testabilidad por sustitución de
  adaptadores que ofrecería hexagonal; se compensa con pruebas de integración
  por módulo.

## Tácticas seleccionadas para los atributos priorizados

| Atributo | Táctica elegida | Costo asumido |
|---|---|---|
| Usabilidad | Filtros visibles en la misma vista de resultados; resultados con info clave sin abrir cada publicación (`docs/aspectos.md`) | Más lógica de presentación a mantener sincronizada con el módulo de búsqueda |
| Seguridad | Control de acceso por tipo de usuario (estudiante/administrador), auditoría de reportes | Fricción adicional de uso, latencia por validaciones |
| Rendimiento | Índice y caché en el módulo de búsqueda | Necesidad de política de invalidación declarada |
| Modificabilidad | SOLID/GRASP dentro de cada módulo; frontera de módulo = frontera de dominio | Más tipos e indirección interna, aceptado por ser el costo menor frente a hexagonal completo |

## Referencia
Motivado por el escenario de calidad de usabilidad en `docs/aspectos.md` y por
la sección "Solution Strategy" de `docs/arc42-template-EN.md`.
