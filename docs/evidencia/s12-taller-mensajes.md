# S12 — Taller de mensajes aplicado a una operación real

## 1. La operación elegida

**Publicar un documento.** Después de persistir los metadatos, el sistema debe avisar a
`administracion` para que el documento entre a su bandeja de revisión. Ese aviso **no** puede hacer
fallar la publicación ni bloquear al estudiante, así que se modela como evento
`documento.publicado`. No es un ejemplo de laboratorio: está en `POST /documentos`.

| Punto del taller | Cómo se resolvió | Artefacto |
|---|---|---|
| 1. Contrato del mensaje | Campos, tipos, obligatoriedad y reglas de compatibilidad | [`../eventos/contrato-evento.md`](../eventos/contrato-evento.md), `documento-publicado.schema.json` |
| 2. Garantía de entrega | **Al menos una vez**; el consumidor es idempotente | [ADR 0015](../adr/0015-mensajeria-asincrona-con-outbox.md) |
| 3. Duplicados | Descarte por `event_id` y por `id_documento` | `ProcesadorIdempotente`, `revision.registrar_para_revision` |
| 4. Reintentos y DLQ | 3 intentos, espera 1 s y 2 s, luego `fallidos` | `app/eventos/outbox.py` |
| 5. Pruebas | Entrega, duplicado, fallo recuperable, DLQ, contrato | `tests/test_eventos.py` |
| 6. Trazabilidad | `event_id` y `correlation_id` en cada log | `app/main.py` (`_JsonFormatter`) |
| 7. Decisión | Outbox vs. llamada síncrona vs. broker | ADR 0015 |
| 8. Límites | Memoria, una instancia, sin orden ni durabilidad | [`../eventos/limites.md`](../eventos/limites.md) |

## 2. Flujo

```text
POST /documentos (token + Idempotency-Key)
   |
   +--> persiste en Firestore
   +--> invalida la caché
   +--> publica documento.publicado (event_id, correlation_id, payload)
   +--> 201/200/409/503  ──────────────► respuesta al administrador
                                              |
                                  BackgroundTasks: despachar
                                              |
                                              v
                              administracion.revision (dedup)
```

Si la publicación se repite con la misma clave, **no** se emite un segundo evento: la prueba
`test_reintentar_la_publicacion_no_emite_un_segundo_evento` lo verifica.

## 3. Contrato y ejemplo

```json
{
  "event_id": "0f9f5c26-6a4b-4a4e-9c1e-8a0f0f7a2b31",
  "tipo": "documento.publicado",
  "version": 1,
  "ocurrido_en": "2026-11-16T14:03:22.481910+00:00",
  "correlation_id": "2f2f0a4e-1d8b-4a0b-9a1e-2c6f0b7d5e10",
  "payload": {"id_documento": 42, "titulo": "Taller de Python", "materia": "Programación", "autor": "Ana"}
}
```

La prueba `test_el_evento_cumple_el_contrato_publicado` valida el mensaje real contra el JSON Schema;
`test_el_contrato_del_evento_rechaza_payload_incompleto` demuestra que el esquema rechaza un payload
sin campos obligatorios. El contrato no es decorativo.

## 4. Demostración reproducible

```bash
# 1. Publicar (con la API local y SHAREU_ADMIN_TOKEN configurado)
curl -X POST http://127.0.0.1:8000/documentos \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: $SHAREU_ADMIN_TOKEN" \
  -H "Idempotency-Key: demo-taller-0001" \
  -d '{"titulo":"Taller de Python","universidad":"UTB","carrera":"Ingeniería de Sistemas","materia":"Programación","tipo":"Taller","autor":"Ana","calificacion":4.5,"palabras_clave":"python"}'

# 2. Ver la bandeja (exige el mismo token)
curl -H "X-Admin-Token: $SHAREU_ADMIN_TOKEN" http://127.0.0.1:8000/administracion/revision

# 3. Ver los contadores del outbox
curl http://127.0.0.1:8000/administracion/eventos

# 4. Repetir el paso 1: responde 200 y NO duplica ni la bandeja ni el evento
```

Los logs muestran la traza completa:

```json
{"message":"evento publicado","event_id":"0f9f…","correlation_id":"2f2f…","tipo_evento":"documento.publicado","intento":0,"estado_evento":"pendiente"}
{"message":"evento procesado","event_id":"0f9f…","correlation_id":"2f2f…","tipo_evento":"documento.publicado","intento":0,"estado_evento":"procesado"}
```

## 5. Fallos demostrables

| Fallo | Cómo se demuestra | Resultado esperado |
|---|---|---|
| Consumidor falla una vez | `test_un_fallo_recuperable_se_reintenta_y_termina_bien` | Reintenta y termina procesado |
| Consumidor falla siempre | `test_agotar_los_intentos_manda_el_evento_a_fallidos` | 3 intentos y DLQ con `ultimo_error` |
| Evento duplicado | `test_un_duplicado_no_crea_dos_entradas_de_revision` | Una sola entrada |
| Publicación repetida | `test_reintentar_la_publicacion_no_emite_un_segundo_evento` | Sin segundo evento |
| Bandeja sin token | `test_la_bandeja_de_revision_sin_token_es_rechazada` | 401/503 |

## 6. Lo que este taller no resuelve

No hay durabilidad: un reinicio pierde pendientes y DLQ. No hay broker ni consumidores externos. No
hay orden garantizado. Todo está declarado en [`../eventos/limites.md`](../eventos/limites.md), con
el criterio para sustituir el outbox cuando el sistema crezca. Presentarlo como mensajería de
producción sería falso; presentarlo como el mecanismo correcto para **esta** escala es defendible.

## 7. Trazabilidad

`docs/aspectos.md` (A4, A7, A10) → ADR 0004, 0015 → `app/eventos/outbox.py`,
`app/administracion/revision.py`, `app/documentos/router.py` → `tests/test_eventos.py` →
[`../eventos/contrato-evento.md`](../eventos/contrato-evento.md) → este documento.
