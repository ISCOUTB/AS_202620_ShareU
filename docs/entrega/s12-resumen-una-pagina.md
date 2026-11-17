# Entrega S12 — resumen de una página

**Tema:** estrategia de datos, caché y taller de mensajes.

**Datos.** Firestore (ADR 0012) encapsulado en `documentos/repository.py`. El id es un entero
reservado con `DocumentReference.create()` (ADR 0011), la decisión de datos más costosa de revertir
porque sale al contrato y al frontend. La tabla operación → garantía está en
[`datos/consistencia.md`](../datos/consistencia.md).

**Caché.** Lista pública en memoria, TTL 60 s, invalidación en cada escritura. Sin invalidación, el
usuario publicaría y no vería su documento hasta 60 s después; por eso la invalidación es la
política y el TTL solo la red de seguridad. Medición: 1,00 → 0,07 lecturas por búsqueda. Limitación:
sin *single-flight*, la caché fría concurrente lee varias veces (21/300).

**Mensajería.** La operación real es publicar. Después de persistir, `documentos` emite
`documento.publicado`; la respuesta no espera al consumidor. Garantía **al menos una vez**,
deduplicación por `event_id` y por `id_documento`, 3 reintentos (1 s y 2 s) y DLQ en memoria. Contrato
versionado en `docs/eventos/`. El outbox no es un broker: se declaran sus límites y cuándo
reemplazarlo.

**Pruebas.** Caché (segunda lectura no va a Firestore, TTL expira, escritura invalida), idempotencia
(reintento no duplica, dos escritores no comparten id, conflicto 409), eventos (entrega, duplicado,
reintento, DLQ, contrato, trazabilidad).

**Enlaces.** [`s12-datos-cache.md`](../evidencia/s12-datos-cache.md),
[`s12-taller-mensajes.md`](../evidencia/s12-taller-mensajes.md),
[`contrato-evento.md`](../eventos/contrato-evento.md), [`limites.md`](../eventos/limites.md),
ADR 0011/0013/0015.
