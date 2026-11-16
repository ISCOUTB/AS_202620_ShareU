# ADR 0015: Mensajería asíncrona con outbox en proceso para `documento.publicado`

- **Estado:** Aceptado
- **Fecha:** noviembre de 2026
- **Aspecto relacionado:** Desacoplamiento / Disponibilidad / Consistencia
- **Origen:** Taller de mensajes S12 (`docs/eventos/contrato-evento.md`,
  `docs/eventos/limites.md`)

## Contexto

Publicar un documento tiene dos efectos: persistir los metadatos (obligatorio para responder) y
poner el documento en la bandeja de revisión de administración (un efecto secundario). Si la
bandeja se actualiza en la misma llamada, un fallo del consumidor hace fallar la publicación o
alarga la respuesta. La operación real elegida por el equipo es **publicar un documento**; no es
un prototipo aislado: está en `POST /documentos`.

## Decisión

1. Después de persistir y **antes** de responder, `documentos.router` publica un evento
   `documento.publicado` en un **outbox en memoria** (`app/eventos/outbox.py`). La respuesta HTTP
   no espera al consumidor.
2. El despacho se ejecuta en `BackgroundTasks`, después de enviar la respuesta.
3. **Garantía: al menos una vez.** El consumidor debe ser idempotente; se asume que un evento
   puede llegar dos veces y que, ante un reinicio, un evento pendiente se pierde (límite
   declarado).
4. **Deduplicación:** `ProcesadorIdempotente` descarta por `event_id`; la bandeja además evita
   duplicar por `id_documento`. Clave: `event_id` (UUID generado por el productor).
5. **Reintentos:** 3 intentos con espera exponencial 1 s, 2 s, 4 s
   (`SHAREU_EVENTO_ESPERA_BASE_SEGUNDOS`); al agotarlos, el evento pasa a la cola de fallidos
   (`fallidos`, una DLQ en memoria) y se registra con `estado_evento=fallido`.
6. **Contrato:** `docs/eventos/documento-publicado.schema.json` y
   `docs/eventos/contrato-evento.md`; versión `1`. Un cambio incompatible sube `version` y exige
   consumidor nuevo.
7. **Trazabilidad:** cada log lleva `event_id`, `correlation_id` (el `request_id` HTTP),
   `tipo_evento`, `intento` y `estado_evento`. Contadores en `GET /administracion/eventos`.

## Opciones evaluadas

### A. Llamada síncrona al consumidor dentro de `POST /documentos` — descartada
- Ventaja: sin infraestructura de eventos; el error se ve en la misma respuesta.
- Desventaja: acopla la disponibilidad de la publicación a la bandeja. Si administración falla, el
  documento ya quedó persistido pero el usuario recibe un error; si se reintenta, hay que resolver
  la idempotencia de dos efectos. Añade latencia al flujo crítico.

### B. Broker real (RabbitMQ, Kafka, Pub/Sub) — descartada por ahora
- Ventaja: entrega duradera, reintentos y DLQ de verdad, desacoplamiento entre procesos.
- Desventaja: un contenedor o servicio más, credenciales, cuotas y operación; el plan gratuito de
  un broker gestionado suele pedir tarjeta. Para una sola instancia y un consumidor local es
  desproporcionado. Criterio de reapertura: cuando haya más de una instancia o el evento deba
  sobrevivir a un reinicio.

### C. Outbox en proceso con deduplicación y DLQ — elegida
- Ventaja: demuestra contrato, garantía, duplicados, reintentos, DLQ y trazabilidad sin añadir
  infraestructura; el productor no se cae si el consumidor falla.
- Desventaja: no es duradero; un reinicio pierde pendientes. Se declara en `limites.md` y no se
  presenta como mensajería de producción.

## Consecuencias

### Positivas
- `POST /documentos` responde 201 aunque la bandeja esté caída; el outbox reintenta.
- Un duplicado no crea dos entradas de revisión (probado en
  `tests/test_eventos.py::test_un_duplicado_no_crea_dos_entradas_de_revision`).
- Un fallo recuperable se reintenta y termina bien
  (`test_un_fallo_recuperable_se_reintenta_y_termina_bien`).

### Negativas
- **Durabilidad:** el outbox vive en memoria. Un reinicio descarta pendientes y la DLQ. En
  producción haría falta persistir el evento en Firestore o usar un broker.
- **Una sola instancia:** dos réplicas tendrían outboxes separados y bandejas separadas.
- **Sin orden garantizado:** los eventos se despachan en el orden de la lista, pero no hay
  particiones ni clave de orden; el consumidor no depende del orden.

## Trazabilidad

`docs/aspectos.md` (A4, A6) → este ADR → `app/eventos/outbox.py`,
`app/administracion/revision.py`, `app/documentos/router.py`, `app/main.py` →
`tests/test_eventos.py`, `tests/test_idempotencia.py` → `docs/eventos/contrato-evento.md`,
`docs/eventos/limites.md` → arc42 §6.3, §8.6.
