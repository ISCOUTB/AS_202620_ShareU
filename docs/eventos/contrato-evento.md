# Contrato del evento `documento.publicado` (versión 1)

Taller de mensajes S12. Este documento es el contrato legible por humanos; la forma
ejecutable está en [`documento-publicado.schema.json`](documento-publicado.schema.json) y la
prueba de que el productor la respeta está en `tests/test_eventos.py`.

## 1. Quién produce y quién consume

| Rol | Módulo | Código | Cuándo |
|---|---|---|---|
| **Productor** | `documentos` | `app/documentos/router.py` → `app.eventos.publicar` | Solo cuando `POST /documentos` **crea** un documento (`creado=True`). Un reintento idempotente no vuelve a emitir el evento |
| **Consumidor** | `administracion` | `app/administracion/revision.registrar_para_revision` | Al despachar el outbox, después de la respuesta HTTP (`BackgroundTasks`) |
| **Cableado** | `app.main` | `eventos.suscribir(...)` | Una sola vez al arrancar, idempotente por nombre |

El productor no importa el consumidor: la suscripción vive en el punto de composición
(`app/main.py`), tal como exige el ADR 0001.

## 2. Forma del mensaje

| Campo | Tipo | Obligatorio | Significado |
|---|---|---|---|
| `event_id` | string (UUID) | sí | Identidad del mensaje y **clave de deduplicación** |
| `tipo` | `"documento.publicado"` | sí | Nombre del evento, congelado en la versión 1 |
| `version` | `1` | sí | Versión del contrato; un cambio incompatible la sube |
| `ocurrido_en` | string (date-time) | sí | Momento de publicación del evento (UTC) |
| `correlation_id` | string | sí | `request_id` de la solicitud HTTP que lo originó; permite seguirlo en los logs |
| `payload.id_documento` | integer ≥ 1 | sí | Id del documento persistido |
| `payload.titulo` | string 1–200 | sí | Título del documento |
| `payload.materia` | string 1–120 | sí | Materia a la que pertenece |
| `payload.autor` | string ≤ 120 o `null` | no | Nombre del autor en el momento de publicar |

`additionalProperties: false` en el esquema: un campo no declarado es un cambio incompatible.

### Ejemplo real

```json
{
  "event_id": "0f9f5c26-6a4b-4a4e-9c1e-8a0f0f7a2b31",
  "tipo": "documento.publicado",
  "version": 1,
  "ocurrido_en": "2026-11-16T14:03:22.481910+00:00",
  "correlation_id": "2f2f0a4e-1d8b-4a0b-9a1e-2c6f0b7d5e10",
  "payload": {
    "id_documento": 42,
    "titulo": "Taller de Python",
    "materia": "Programación",
    "autor": "Ana"
  }
}
```

## 3. Garantía de entrega y lo que el consumidor debe asumir

- **Garantía: al menos una vez.** El outbox reintenta y la reentrega es posible por diseño
  (`eventos.reenviar` la simula en pruebas y en la demo).
- **El consumidor es idempotente por `event_id`** (`ProcesadorIdempotente`). Además, la bandeja
  comprueba `id_documento`, de modo que un evento con otro `event_id` para el mismo documento
  tampoco duplica la entrada.
- **No hay orden garantizado.** El consumidor no depende del orden de los eventos.
- **No hay entrega duradera.** El outbox vive en memoria: un reinicio descarta pendientes y la
  cola de fallidos. Se declara en [`limites.md`](limites.md).
- **Sin consumidores no es un fallo:** el evento queda pendiente hasta que alguien se suscriba
  (`_entregar` devuelve `False` sin contar un intento).

## 4. Reglas de compatibilidad

| Cambio | ¿Compatible? | Qué exige |
|---|---|---|
| Agregar un campo **opcional** al `payload` | Sí | Actualizar el esquema y el consumidor, sin subir `version` |
| Agregar un campo obligatorio | **No** | Subir `version` y publicar un evento nuevo; el consumidor viejo no lo entiende |
| Quitar o renombrar un campo | **No** | Subir `version`; los consumidores viejos quedarían con campos ausentes |
| Cambiar el tipo de un campo (`integer` → `string`) | **No** | Subir `version` |
| Cambiar el significado de un campo sin cambiar el tipo | **No** | Subir `version`; el consumidor interpretaría mal el valor |
| Cambiar `tipo` o el nombre del evento | **No** | Evento nuevo con su propio contrato |
| Cambiar la garantía a «exactamente una vez» | **No** | Es una propiedad del transporte, no del esquema; exige broker y ADR nuevo |

La disciplina es la misma que la del contrato HTTP (`docs/api/openapi.yaml`): el contrato se
escribe primero y una prueba lo hace cumplir.

## 5. Reintentos, fallos y trazabilidad

| Situación | Comportamiento | Dónde se ve |
|---|---|---|
| El consumidor lanza una excepción | Se incrementa `intentos`, se reprograma con espera 1 s y 2 s | Log `evento reprogramado`, contador `reintentos` |
| Se agotan los 3 intentos | El evento pasa a la cola de fallidos (DLQ en memoria) con `ultimo_error` | Log `evento enviado a la cola de fallidos`, contador `fallidos` |
| Llega un duplicado | Se descarta por `event_id` | Log `evento duplicado descartado`, contador `duplicados` |
| El payload no trae `id_documento`, `titulo` o `materia` | El consumidor lanza `ValueError` y entra al flujo de reintentos | `registrar_para_revision` |

Cada línea de log del outbox lleva `event_id`, `correlation_id`, `tipo_evento`, `intento` y
`estado_evento`; los contadores se consultan en `GET /administracion/eventos`. Ejemplo de las dos
líneas que permiten seguir un evento de extremo a extremo:

```json
{"level":"INFO","logger":"shareu.eventos","message":"evento publicado","event_id":"0f9f…","correlation_id":"2f2f…","tipo_evento":"documento.publicado","intento":0,"estado_evento":"pendiente"}
{"level":"INFO","logger":"shareu.eventos","message":"evento procesado","event_id":"0f9f…","correlation_id":"2f2f…","tipo_evento":"documento.publicado","intento":0,"estado_evento":"procesado"}
```

## 6. Pruebas que sostienen el contrato

| Propiedad | Prueba |
|---|---|
| Publicar entrega el evento al consumidor | `test_publicar_entrega_el_evento_al_consumidor` |
| Reintentar la publicación no emite un segundo evento | `test_reintentar_la_publicacion_no_emite_un_segundo_evento` |
| Un duplicado no crea dos entradas de revisión | `test_un_duplicado_no_crea_dos_entradas_de_revision` |
| Un fallo recuperable se reintenta y termina bien | `test_un_fallo_recuperable_se_reintenta_y_termina_bien` |
| Agotar los intentos manda el evento a fallidos | `test_agotar_los_intentos_manda_el_evento_a_fallidos` |
| La bandeja sin token es rechazada | `test_la_bandeja_de_revision_sin_token_es_rechazada` |

## 7. Trazabilidad

`docs/aspectos.md` (A4, A10) → [ADR 0015](../adr/0015-mensajeria-asincrona-con-outbox.md) →
`app/eventos/outbox.py`, `app/documentos/router.py`, `app/administracion/revision.py` →
`docs/eventos/documento-publicado.schema.json` → este documento → `docs/eventos/limites.md` →
`docs/evidencia/s12-taller-mensajes.md`.
