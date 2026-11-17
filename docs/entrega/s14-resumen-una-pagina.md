# Entrega S14 — resumen de una página

**Tema:** medición final e incorporación de la revisión de pares.

**Resultado.** Con caché, la búsqueda medida da **p95 67,54 ms**, **0 % de error** y **0,07
lecturas Firestore/búsqueda**, frente a **72,15 ms**, **0 %** y **1,00** sin caché. Los tres
umbrales de arc42 §10 se cumplen en el entorno medido (ASGI en proceso, Firestore falso).

**Comparación justa.** Misma herramienta, mismos datos, misma concurrencia; solo cambia el TTL. La
línea base se obtiene con `--sin-cache`, sin tocar el código. Artefactos JSON y Markdown versionados.

**Límites.** El modo ASGI no incluye red ni Firestore reales: 67 ms es un límite inferior. El
despliegue respondía 404 al 2026-11-16, así que no hay corrida `--url` ni se presenta como
verificado. La caché fría concurrente produce *stampede* (21/300); se acepta.

**Revisión de pares.** Se incorporaron los hallazgos de infraestructura, ADR, rutas canónicas,
arc42/C4/README, modos de fallo, taller de mensajes, bandeja protegida y `next`. Quedan **abiertos**
solo los que dependen de acciones humanas: empujar la corrección del workflow (los runs #44–#47
fallaron sin jobs por `secrets` en un `if`), configurar `SONAR_TOKEN` y verificar las URLs
desplegadas. El Quality Gate público está en **ERROR** y se declara con sus métricas; la tabla
completa está en arc42 §11.3 y §11.5.

**Mensaje para la sustentación.** «Cumple en la medición local reproducible; el despliegue está
pendiente de verificación.» No se atribuye al sistema lo que no se midió.

**Enlaces.** [`s14-medicion.md`](../evidencia/s14-medicion.md),
[`s14-local-asgi.md`](../evidencia/mediciones/s14-local-asgi.md), arc42 §10–§11, ADR 0016.
