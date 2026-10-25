# Modos de fallo, idempotencia y saga — Evidencia S11

## Integración principal

La única llamada de red que existe en el código es **Aplicación web (Next.js, Vercel) → API backend (FastAPI, Render)**:
`GET /busqueda/documentos`.

- Cliente: `app/frontend/lib/api.ts` (`buscarDocumentos`) y `app/frontend/app/page.tsx` (`buscar`).
- Servidor: `app/busqueda/router.py` → `busqueda.service` → `documentos.service` (todo in-process, ADR 0001).

Es el flujo del escenario prioritario de usabilidad (`docs/aspectos/aspectos.md`). Las integraciones con
almacenamiento y correo aún no tienen código; se tratan al final como pendiente declarado (ADR 0004).

## Tabla de modos de fallo

| Modo | Causa concreta en ShareU | Efecto sin mitigación | Mitigación asignada | Estado | Prueba |
|---|---|---|---|---|---|
| **No responde** | Backend de Render caído o reiniciando; red del estudiante | La búsqueda falla y la pantalla queda sin resultados | 1) `catch` en `page.tsx` muestra «No se pudo conectar con el backend». 2) Un reintento tras 1 s ante error de red o 5xx (`api.ts`). 3) `GET /health` para que la plataforma reinicie el servicio | 1 y 2 implementadas. 3: `/health` existe; `Dockerfile`/`render.yaml` siguen pendientes (hallazgo E3 de `evidencia-s9.md`) | Sin prueba automatizada (el frontend no tiene runner). **Pendiente** |
| **Responde tarde** | Render Free «duerme» tras inactividad y el primer request tarda (README, ADR 0006) | «Buscando…» indefinido; el estudiante no sabe si esperar | Timeout de 15 s por intento con `AbortController`; si vence, cuenta como «no responde» y entra al reintento; luego mensaje de error | Implementada | Sin prueba automatizada. **Pendiente** |
| **Responde dos veces** | Doble clic en «Buscar»; reintento tras timeout cuando el primer intento sí llegó al servidor; doble ejecución del efecto de React en desarrollo | Dos respuestas, posiblemente fuera de orden, pisan el estado de la pantalla | La búsqueda es un `GET` de solo lectura: repetirla devuelve lo mismo y no cambia datos (idempotente por naturaleza). La pantalla ignora respuestas obsoletas (contador de solicitud en `page.tsx`). Efecto aceptado: `registrar_busqueda` cuenta la repetición dos veces (la métrica es indicativa, ADR 0008) | Implementada | `tests/test_resiliencia.py` (3 pruebas) |

Resumen para el proyecto final: **con prueba** → «responde dos veces»; **implementados pero sin prueba** →
«no responde» y «responde tarde» (requieren un runner de pruebas de frontend, fuera del alcance simple de este corte).

## Idempotencia

**Hoy no hay operaciones de escritura expuestas por la API**; solo `GET`. Por eso no se diseña un mecanismo
de idempotencia sobre el flujo actual: el `GET` ya es idempotente. La única escritura (`_initialize` en
`app/documentos/repository.py`) también lo es: `CREATE TABLE IF NOT EXISTS` e inserción de datos semilla solo
si `COUNT(*) == 0`.

Diseño reservado para cuando existan escrituras (una restricción en la base, sin infraestructura nueva):

| Operación futura | Cómo se hace repetible sin duplicar |
|---|---|
| Calificar un documento (`calificaciones`, ADR 0003) | Restricción única `(documento_id, usuario_id)` y escritura como *upsert*: repetir deja el mismo estado |
| Publicar un documento (`documentos` + almacenamiento, ADR 0004) | El frontend genera un UUID por intento de publicación y lo envía como `Idempotency-Key`; `documentos` lo guarda en una columna única; repetir devuelve el documento ya creado |

## Saga

**No aplica hoy**: no hay transacciones entre componentes distribuidos. Los cinco módulos comparten un proceso
y una base de datos; no hay una operación que necesite deshacerse en otro servicio.

**Único caso futuro: publicar documento** (almacenamiento externo + metadatos en SQLite). Se resuelve como una
saga mínima de dos pasos, sin orquestador:

1. Guardar el archivo en el almacenamiento (síncrono, con timeout; ADR 0004).
2. Registrar los metadatos en `documentos`.
3. Si el paso 2 falla, **compensación**: borrar el archivo del paso 1. Si la compensación también falla, el archivo
   huérfano se acepta (costo bajo) y se registra en el log para limpieza manual.

El orden «archivo primero, metadatos después» evita metadatos que apunten a un archivo inexistente.

## Pendiente declarado: integraciones futuras (sin código)

| Integración | No responde | Responde tarde | Responde dos veces |
|---|---|---|---|
| Backend → almacenamiento (síncrona) | La publicación se rechaza con error claro; no se crea el registro | Timeout de 10 s; se rechaza | `Idempotency-Key` (ver arriba) |
| Backend → correo (asíncrona, outbox) | El evento queda pendiente en el outbox | No bloquea la operación principal | Entrega al menos una vez; cada evento lleva `event_id` y un campo `enviado_en` para no reenviar lo ya enviado |

Reintentos del correo: espera creciente (1 min, 5 min, 30 min), máximo 5 intentos; luego el evento se marca `fallido`.
Se implementa cuando el módulo de notificaciones entre en un corte (ADR 0004, reglas 4 y 5).
