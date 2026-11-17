---
date: noviembre 2026
title: "Documentación de arquitectura ShareU — arc42"
---

# ShareU — documentación de arquitectura (arc42)

| Sección | Contenido |
|---|---|
| [1. Introducción y objetivos](01-introduccion-y-objetivos.md) | Qué es ShareU y qué calidad persigue |
| [2. Restricciones](02-restricciones-arquitectonicas.md) | Stack, costo, despliegue y reglas del curso |
| [3. Contexto y alcance](03-contexto-y-alcance.md) | Actores, sistemas externos y fronteras |
| [4. Estrategia de solución](04-estrategia-de-solucion.md) | Monolito modular, Firestore, caché, outbox, seguridad |
| [5. Bloques de construcción](05-vista-de-bloques-de-construccion.md) | Módulos, composición y responsabilidades |
| [6. Vista de ejecución](06-vista-de-ejecucion.md) | Buscar, publicar, consumir el evento y fallar |
| [7. Vista de despliegue](07-vista-de-despliegue.md) | Docker, Dokploy, Firestore y CI |
| [8. Conceptos transversales](08-conceptos-transversales.md) | Persistencia, consistencia, seguridad, observabilidad |
| [9. Decisiones arquitectónicas](09-decisiones-arquitectonicas.md) | Los 16 ADR |
| [10. Requisitos de calidad](10-requisitos-de-calidad.md) | Escenario medible, umbrales y evidencia |
| [11. Riesgos y deuda técnica](11-riesgos-y-deuda-tecnica.md) | Riesgos, límites y revisión de pares |
| [12. Glosario](12-glosario.md) | Términos del dominio y de arquitectura |

Documentos de apoyo: [`../aspectos.md`](../aspectos.md) (trazabilidad de aspectos),
[`../c4/nivel-2.md`](../c4/nivel-2.md) (contenedores), [`../datos/consistencia.md`](../datos/consistencia.md),
[`../eventos/contrato-evento.md`](../eventos/contrato-evento.md),
[`../seguridad/amenazas.md`](../seguridad/amenazas.md),
[`../resiliencia/modos-de-fallo.md`](../resiliencia/modos-de-fallo.md), [`../ia.md`](../ia.md).
