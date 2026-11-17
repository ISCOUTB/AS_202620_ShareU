# 9. Decisiones arquitectónicas

Todas las decisiones están en [`../adr/`](../adr/) con contexto, alternativa descartada,
consecuencias y criterio de reapertura.

| ADR | Decisión | Estado | Aspecto |
|---|---|---|---|
| [0001](../adr/0001-estilo-arquitectonico.md) | Monolito modular con fronteras por módulo | Aceptado | Mantenibilidad |
| [0002](../adr/0002-usabilidad-busqueda-en-una-solicitud.md) | Búsqueda combinada en una sola solicitud | Aceptado | Usabilidad |
| [0003](../adr/0003-separacion-contexto-calificaciones.md) | Separar el contexto de Calificaciones de Documentos | Propuesto (no implementado) | Integridad |
| [0004](../adr/0004-integracion-sincrona-y-asincrona.md) | Almacenamiento síncrono; efectos secundarios asíncronos | Aceptado | Disponibilidad |
| [0005](../adr/0005-migracion-frontend-nextjs.md) | Frontend Next.js y retiro del sitio estático | Aceptado | Mantenibilidad |
| [0006](../adr/0006-plataforma-backend-despliegue.md) | Backend en Docker/Dokploy (no Render) | Aceptado | Costo / Operación |
| [0007](../adr/0007-plataforma-frontend-despliegue.md) | Frontend en Docker/Dokploy (no Vercel) | Aceptado | Costo / Operación |
| [0008](../adr/0008-metrica-tras-interfaz-de-administracion.md) | Métrica de búsquedas tras la interfaz de administración | Aceptado | Mantenibilidad |
| [0009](../adr/0009-no-incorporar-componente-generativo.md) | No incorporar un componente generativo | Aceptado | Alcance / Costo |
| [0010](../adr/0010-no-extraer-modulos.md) | No extraer módulos a servicios | Aceptado | Modificabilidad |
| [0011](../adr/0011-identidad-de-datos-y-propiedad-por-modulo.md) | Id entero reservado; referencias por id entre módulos | Aceptado | Integridad (decisión de datos más costosa de revertir) |
| [0012](../adr/0012-persistencia-en-firestore.md) | Persistencia en Firestore | Aceptado | Disponibilidad / Costo |
| [0013](../adr/0013-cache-de-lectura-con-invalidacion.md) | Caché de lectura con TTL e invalidación por escritura | Aceptado | Rendimiento / Costo |
| [0014](../adr/0014-endurecimiento-http-y-escritura-autenticada.md) | Token administrativo fail-closed y cabeceras | Aceptado | Seguridad |
| [0015](../adr/0015-mensajeria-asincrona-con-outbox.md) | Outbox en proceso, al menos una vez y DLQ | Aceptado | Desacoplamiento |
| [0016](../adr/0016-medicion-de-latencia-y-costo-de-lecturas.md) | Medir p95, error y lecturas por búsqueda | Aceptado | Rendimiento / Costo |

## 9.1 Relaciones entre ADR

- **0001** es la decisión base: las demás se interpretan dentro del monolito modular.
- **0012** reemplaza la parte de persistencia de **0006** (SQLite sin disco persistente).
- **0011** fija los ids que **0012** necesita; juntos sostienen la publicación idempotente.
- **0013** y **0015** son mecanismos en proceso que **0006** permite al desplegar una instancia.
- **0014** es transitorio hasta que **0003**/`usuarios` estén implementados.
- **0016** es la vara con la que se mide **0013**.

## 9.2 ADR que se reabren

- **0003**: cuando `calificaciones` entre en alcance.
- **0012**: si el catálogo o el costo de Firestore dejan de justificarse.
- **0013**: si el TTL ya no acota una inconsistencia aceptable o si hay más de una instancia.
- **0015**: con más de una instancia o si el evento debe sobrevivir a un reinicio.
- **0016**: si el umbral cambia o si el despliegue permite medir con `--url`.
