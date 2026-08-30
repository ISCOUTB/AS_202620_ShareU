# ADR 0001: Estilo arquitectónico de ShareU

- **Estado:** Aceptado
- **Fecha:** agosto de 2026

## Contexto

ShareU es una plataforma web para compartir material académico entre
estudiantes universitarios, organizada por universidad, carrera y materia.

El aspecto de calidad crítico es la **usabilidad**: el estudiante debe poder
encontrar un documento relevante en menos de 3 interacciones mediante búsqueda
y filtrado. Los siguientes atributos prioritarios son seguridad, rendimiento y
disponibilidad; mantenibilidad y escalabilidad tienen prioridad media.

El sistema tiene dominios claramente separables: usuarios, documentos,
búsqueda, calificaciones y administración. El equipo es reducido y el proyecto
se desarrolla de forma incremental, por lo que se necesita una arquitectura
que permita entregar funcionalidad sin introducir desde el principio la
complejidad de un sistema distribuido.

El escenario que conduce esta decisión está documentado en
[`docs/aspectos/aspectos.md`](../aspectos/aspectos.md).

## Decisión

Se adopta un **monolito modular**: un único desplegable organizado por
módulos de dominio, con fronteras explícitas y comunicación controlada.

Los módulos son:

- `usuarios`
- `documentos`
- `busqueda`
- `calificaciones`
- `administracion`

Cada módulo es responsable de su dominio. Los accesos entre módulos se realizan
mediante interfaces de servicio; un módulo no debe acceder directamente a las
tablas internas de otro.

## Alternativas consideradas

### Capas (N-tier) — descartada

Favorece la simplicidad inicial, pero la frontera principal es técnica
(presentación, lógica y datos). Esto puede concentrar las reglas de búsqueda,
calificación y moderación en capas compartidas y producir cambios
transversales.

**Criterio de reapertura:** podría reconsiderarse si el dominio se simplifica
de forma que las fronteras de dominio dejen de aportar valor.

**Consecuencia de descartarla:** se acepta mantener una estructura algo más
orientada a dominios para reducir cambios transversales.

### Hexagonal (puertos y adaptadores) — descartada por ahora

Ofrece mayor testabilidad y facilita sustituir infraestructura, pero introduce
más indirección y una curva de aprendizaje que el equipo no necesita asumir
en esta fase.

**Criterio de reapertura:** se reconsiderará si aparece una necesidad concreta
de sustituir infraestructura con frecuencia, aislar múltiples adaptadores o
aumentar la testabilidad mediante puertos y adaptadores.

**Consecuencia de descartarla:** se obtiene menor aislamiento de infraestructura
que con hexagonal; se compensa inicialmente con pruebas de integración y una
frontera explícita entre módulos.

## Consecuencias

### Positivas

- La estructura del código refleja los dominios del negocio.
- La búsqueda puede evolucionar sin reorganizar todo el backend.
- Se mantiene un único despliegue sencillo para el equipo.
- Existe una ruta futura para extraer un módulo si aparece una necesidad real.

### Negativas

- El equipo debe vigilar el acoplamiento entre módulos.
- Un monolito no permite escalar cada dominio de manera independiente desde
  el inicio.
- Hay menos aislamiento de infraestructura que en una arquitectura hexagonal.

## Tácticas seleccionadas

| Atributo | Táctica | Costo asumido |
|---|---|---|
| Usabilidad | Filtros visibles y resultados con información clave | Mayor lógica que mantener en búsqueda |
| Seguridad | Control de acceso por rol y auditoría de reportes | Validaciones adicionales |
| Rendimiento | Filtrado eficiente, índices y posible caché | Complejidad de invalidación |
| Modificabilidad | SOLID/GRASP dentro de cada módulo y fronteras de dominio | Más estructura interna |

## Reglas de implementación

1. Cada módulo mantiene su responsabilidad de dominio.
2. La persistencia de un dominio pertenece a su módulo.
3. Otro módulo consume servicios públicos, no tablas internas.
4. Las dependencias nuevas entre módulos deben justificarse en revisión de
   código.
5. Si se plantea extraer un módulo a un servicio independiente, debe abrirse
   un nuevo ADR o revisarse este ADR con evidencia.

## Referencias

- Escenario: [`docs/aspectos/aspectos.md`](../aspectos/aspectos.md)
- Estrategia: [`docs/arc42/arc42.md`](../arc42/arc42.md)
- C4 nivel 2: [`docs/c4/nivel-2.md`](../c4/nivel-2.md)
