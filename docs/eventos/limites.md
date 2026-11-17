# Límites del outbox y de la mensajería actual

Este documento declara **lo que el mecanismo de eventos no hace**. Presentar el outbox en proceso
como mensajería de producción sería falso; la ficha S12 pide, además del contrato y la garantía,
los límites y el criterio para reabrir la decisión (ADR 0015).

## 1. Qué es y qué no es

| Propiedad | Estado real | Consecuencia |
|---|---|---|
| **Durabilidad** | En memoria (`_pendientes`, `_fallidos`) | Un reinicio o un despliegue pierde eventos pendientes y la DLQ |
| **Entrega** | Al menos una vez, dentro del proceso | El consumidor debe deduplicar; puede ver el mismo `event_id` dos veces |
| **Orden** | El de la lista de pendientes; sin particiones ni clave | El consumidor no depende del orden |
| **Escalado** | Una instancia = un outbox y una bandeja | Dos réplicas tendrían outboxes y bandejas separados |
| **Despacho** | `BackgroundTasks` después de la respuesta | Si el proceso muere antes de despachar, el evento se pierde |
| **Reintentos** | 3 intentos con espera 1 s y 2 s | No hay reintento manual desde la API; `reenviar` existe para pruebas y demo |
| **DLQ** | Lista en memoria, consultable por código | No hay reproceso automático ni inspección HTTP de la DLQ |
| **Backpressure** | Ninguna | `publicar` no bloquea: si el proceso publica más de lo que despacha, la lista crece |
| **Observabilidad** | Contadores y logs JSON | No hay trazas distribuidas ni métricas Prometheus |
| **Multiproceso** | No soportado | Un `uvicorn --workers N` tendría N outboxes y N bandejas |

## 2. Qué pasa en cada fallo

| Fallo | Qué ocurre | Qué queda inconsistente | Cómo se recupera |
|---|---|---|---|
| El consumidor falla una vez | Se reintenta con espera creciente | Nada: el documento existe y la entrada de revisión llega después | Automático (hasta 3 intentos) |
| El consumidor falla 3 veces | El evento va a la DLQ en memoria | El documento existe pero no está en la bandeja | Manual: revisar la DLQ en código/logs y reencolar; en producción, reconstruir desde Firestore |
| El proceso muere tras responder y antes de despachar | El evento se pierde | Documento publicado sin entrada en la bandeja | Manual: la bandeja puede reconstruirse consultando Firestore por documentos sin revisar (trabajo futuro) |
| El proceso se reinicia con eventos pendientes | Se pierden los pendientes y la DLQ | Posibles documentos sin aviso | Manual, igual que arriba |
| Llega un duplicado | Se descarta por `event_id` y por `id_documento` | Nada | Automático |
| Dos instancias | Cada una tiene su outbox y su bandeja | Un administrador puede ver solo parte de la bandeja | Fuera del alcance actual: el despliegue es una instancia |

## 3. Por qué se acepta

El consumidor es una **bandeja de moderación**, no un movimiento de dinero ni un stock. Perder un
aviso no destruye el documento: el material sigue persistido y la bandeja es reconstruible. El
costo de un broker real (contenedor o servicio gestionado, credenciales, cuotas, tarjeta) no se
justifica para una instancia y un consumidor local, y la restricción del curso es USD 0/mes sin
tarjeta (ADR 0006). La alternativa síncrona también se evaluó y se descartó porque acopla la
disponibilidad de la publicación a la bandeja (ADR 0015).

## 4. Criterio de reapertura

Se debe reemplazar el outbox en memoria por una implementación duradera cuando ocurra **cualquiera**
de estas condiciones:

1. El despliegue pasa a **más de una instancia** o a workers separados.
2. El evento debe **sobrevivir a un reinicio** (por ejemplo, una notificación al autor que no se
   puede perder).
3. Aparece un consumidor externo (correo, webhook, otro servicio) que no comparte el proceso.
4. El volumen hace que la lista en memoria o el despacho en `BackgroundTasks` sea un cuello de
   botella.

La sustitución natural es persistir el evento en una colección `eventos` de Firestore antes de
responder y despachar con un proceso que reclame pendientes, o un broker gestionado si el
presupuesto lo permite. En ambos casos se conserva este contrato: `event_id`, `version`,
deduplicación y DLQ.

## 5. Lo que sí está probado

`tests/test_eventos.py` cubre: publicación y consumo, reintento de un fallo recuperable, DLQ al
agotar intentos, deduplicación por `event_id` y por `id_documento`, ausencia de un segundo evento
en un reintento idempotente de la publicación, y rechazo de la bandeja sin token. Lo que **no**
está probado es la durabilidad, porque el diseño no la ofrece.

## 6. Trazabilidad

[ADR 0015](../adr/0015-mensajeria-asincrona-con-outbox.md) → `app/eventos/outbox.py` →
[`contrato-evento.md`](contrato-evento.md) → este documento →
`docs/evidencia/s12-taller-mensajes.md` → `docs/aspectos.md` (A10).
