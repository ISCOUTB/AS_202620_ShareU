# Aspectos de calidad

## Idea del proyecto

ShareU es una plataforma web para estudiantes universitarios. Permite
compartir y encontrar apuntes, ejercicios, talleres, parciales y otros
documentos organizados por universidad, carrera y materia.

## Aspecto declarado: Usabilidad

La usabilidad es el aspecto de calidad prioritario porque el valor principal de
ShareU depende de que un estudiante pueda encontrar material académico de
forma ágil.

### Escenario de calidad

| Elemento | Descripción |
|---|---|
| **Fuente del estímulo** | Un estudiante universitario que utiliza ShareU |
| **Estímulo** | El estudiante ingresa buscando material académico específico |
| **Artefacto** | Módulo de búsqueda y filtrado |
| **Entorno** | Uso normal desde computador o celular, con o sin experiencia previa |
| **Respuesta** | El sistema permite combinar filtros y muestra resultados relevantes con información clave |
| **Medida de respuesta** | El usuario logra encontrar un documento relevante en menos de 3 interacciones (clics/filtros), sin ayuda externa |

### Tácticas

- Filtros visibles en la misma vista de resultados.
- Búsqueda por palabra clave.
- Información clave visible en cada resultado: título, materia, tipo, autor
  y calificación.
- Diseño responsivo para priorizar el uso desde dispositivos móviles.
- Mensajes claros cuando no existen resultados.

### Forma de verificación

Se comprobará el escenario mediante pruebas de usabilidad con estudiantes y
revisión heurística de la interfaz. En el backend, el corte vertical permite
combinar los filtros en una única solicitud, evitando pasos innecesarios.

## Comparación que motiva la decisión arquitectónica

El escenario anterior es el conductor principal del ADR 0001. La siguiente
matriz compara las alternativas consideradas:

| Atributo | Escenario / necesidad | Capas (N-tier) | Hexagonal | Monolito modular | Beneficio esperado | Costo / consecuencia | Decisión |
|---|---|---|---|---|---|---|---|
| Usabilidad | Encontrar material en menos de 3 interacciones | Puede funcionar, pero no define bien las fronteras de búsqueda | Facilita pruebas, pero añade indirección | Permite evolucionar búsqueda como dominio propio | Búsqueda aislada y fácil de modificar | Requiere disciplina entre módulos | **Elegido** |
| Modificabilidad | Cambiar reglas de búsqueda sin afectar calificaciones | Cambios transversales entre capas | Alta | Alta por dominio | Menor impacto de cambios | Más estructura que un monolito simple | **Elegido** |
| Testabilidad | Validar el flujo de búsqueda | Media | Alta | Alta con pruebas de integración | Pruebas directas del módulo | Menor sustitución de adaptadores que hexagonal | **Aceptado** |
| Simplicidad | Entrega incremental semanal | Alta al principio | Baja por mayor indirección | Alta | Implementación gradual | Hay que mantener límites explícitos | **Elegido** |
| Curva de aprendizaje | Equipo reducido | Baja | Alta | Media | Permite aplicar la arquitectura sin infraestructura distribuida | Requiere conocer fronteras de dominio | **Elegido** |
| Rendimiento | Responder rápidamente a búsquedas | Adecuado | Adecuado | Adecuado | Permite optimizar búsqueda de forma localizada | Caché/índices deben mantenerse | **Elegido** |
| Escalabilidad | Crecimiento progresivo de usuarios/documentos | Media | Alta | Media/alta | Permite extraer un módulo si aparece necesidad | No escala cada dominio de forma independiente desde el inicio | **Elegido** |
| Seguridad | Controlar acceso y responsabilidades | Adecuado | Adecuado | Adecuado | Fronteras de dominio facilitan ubicar controles | Deben revisarse permisos en cada módulo | **Elegido** |

## Trazabilidad

El escenario de usabilidad motiva la estrategia de solución de
[`docs/arc42/arc42.md`](../arc42/arc42.md) y la decisión formal de
[`docs/adr/0001-estilo-arquitectonico.md`](../adr/0001-estilo-arquitectonico.md).

El corte vertical que implementa esta estrategia está descrito en
[`docs/c4/nivel-2.md`](../c4/nivel-2.md).
