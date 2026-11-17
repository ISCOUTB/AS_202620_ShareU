# S11 — Fallos parciales, idempotencia y decisión de no extraer

## 1. Qué se revisó

La ficha S11 pide analizar qué pasa cuando una integración falla **parcialmente**: no responde,
responde tarde o responde dos veces. El análisis se hizo sobre las dos integraciones reales
(navegador→API y API→Firestore) y sobre el efecto asíncrono (outbox→bandeja), no solo sobre la
primera. El resultado completo está en [`../resiliencia/modos-de-fallo.md`](../resiliencia/modos-de-fallo.md).

## 2. Matriz de fallos y cobertura

| Integración | No responde | Responde tarde | Responde dos veces |
|---|---|---|---|
| Navegador → API | Mensaje de error + 1 reintento; **sin prueba de navegador** | Timeout 15 s; **sin prueba de navegador** | GET idempotente + descarte de respuestas viejas; `tests/test_resiliencia.py` |
| API → Firestore | Timeout 2 s × 3 → 503; `test_timeout_se_reporta_como_error_de_persistencia` | Timeout + reintentos; misma prueba y medición S14 | `Idempotency-Key` + hash; 4 pruebas de idempotencia |
| Outbox → bandeja | Reintentos 1-2-4 s → DLQ; 2 pruebas | `BackgroundTasks`, no bloquea; prueba de entrega | Deduplicación por `event_id` y `id_documento`; prueba de duplicado |

**Lectura honesta:** los fallos del borde de persistencia y del outbox tienen prueba automatizada.
Los del navegador están implementados y se verificaron por revisión de código, pero **no** hay un
runner de pruebas de navegador en el proyecto. No se presentan como probados.

## 3. Idempotencia implementada

`POST /documentos` exige `Idempotency-Key`. Antes de crear, `_buscar_por_idempotencia` busca la
clave y compara el SHA-256 del cuerpo:

| Caso | Respuesta | Efecto |
|---|---|---|
| Clave nueva, cuerpo válido | **201** | Crea y emite `documento.publicado` |
| Misma clave, mismo cuerpo | **200** | Devuelve el documento; **no** emite otro evento |
| Misma clave, cuerpo distinto | **409** | No crea nada |
| Sin token / token inválido | **401** o **503** | No llega a Firestore |

La reserva del id usa `DocumentReference.create()`, que falla con `AlreadyExists` si otro escritor
tomó el id; el repositorio prueba el siguiente candidato. Así dos publicaciones concurrentes no
comparten id, aunque el contador `max + 1` se haya calculado a la vez.

## 4. Por qué no se usa una saga

Publicar es **una** escritura en Firestore; el aviso a la bandeja es un efecto secundario
recuperable. Si el aviso no llega, el documento sigue válido y la bandeja se puede reconstruir: no
hay nada que compensar. Una saga solo tendría sentido con «guardar archivo + registrar metadatos»,
flujo que **no está implementado**. Se documenta como diseño futuro, no como si existiera.

## 5. Decisión de no extraer módulos

Se evaluó extraer `busqueda` (o `documentos`) como servicio independiente. Se descartó: una sola
instancia, sin equipos separados, sin necesidad de escalado independiente y con el costo de
operación de un despliegue más. El criterio de reapertura está en
[ADR 0010](../adr/0010-no-extraer-modulos.md). Las fronteras ya están preparadas: los módulos se
hablan por `service.py` y `tests/test_fronteras.py` impide cruces.

## 6. Evidencia ejecutable

```bash
pytest tests/test_resiliencia.py tests/test_idempotencia.py tests/test_eventos.py -q
```

Resultado de la última corrida completa: **77 pruebas en verde**. Las pruebas que cubren esta ficha
son las citadas en la matriz de §2.

## 7. Trazabilidad

`docs/aspectos.md` (A3, A4, A6) → ADR 0004, 0010, 0011, 0015 → `app/documentos/repository.py`,
`app/eventos/outbox.py` → pruebas citadas → este documento.
