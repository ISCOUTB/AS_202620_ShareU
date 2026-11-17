# Entrega S11 — resumen de una página

**Tema:** fallos parciales, idempotencia y decisión de no extraer módulos.

**Integraciones analizadas.** Dos reales: navegador → frontend → API y API → Firestore; más el
efecto asíncrono outbox → bandeja. No se analiza solo la primera porque desde ADR 0012 la llamada
de red que domina el flujo es backend → Firestore.

**Modos de fallo.**

| Integración | No responde | Responde tarde | Responde dos veces |
|---|---|---|---|
| Navegador → API | Error visible + 1 reintento | Timeout 15 s | GET idempotente + descarte de respuestas viejas |
| API → Firestore | Timeout 2 s × 3 → 503 | Timeout + reintentos | `Idempotency-Key` + hash; 200/409 |
| Outbox → bandeja | Reintentos 1-2-4 s → DLQ | `BackgroundTasks` no bloquea | Dedup por `event_id` e `id_documento` |

**Idempotencia de publicar.** Misma clave y mismo cuerpo → 200 con el documento existente y sin
segundo evento; misma clave y otro cuerpo → 409; sin token → 401/503. La reserva de id usa
`DocumentReference.create()` atómico y prueba el siguiente ante `AlreadyExists`.

**Saga.** No se usa: publicar es una escritura y el aviso a la bandeja es recuperable, no
compensable. La saga se reserva para «archivo + metadatos», que no está implementado.

**No extraer módulos.** Se evaluó y se descartó: una instancia, sin equipos separados, sin necesidad
de escalado independiente. Las fronteras ya están listas (`service.py`, `test_fronteras.py`); el
criterio de reapertura está en ADR 0010.

**Cobertura honesta.** Persistencia y outbox tienen pruebas automatizadas; los fallos del navegador
están implementados y revisados en código, pero no hay runner de navegador. No se presentan como
probados.

**Enlaces.** [`modos-de-fallo.md`](../resiliencia/modos-de-fallo.md),
[`s11-fallos-parciales.md`](../evidencia/s11-fallos-parciales.md), ADR 0004/0010/0011/0015.
