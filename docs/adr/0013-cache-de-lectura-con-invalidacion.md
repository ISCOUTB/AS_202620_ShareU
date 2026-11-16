# ADR 0013: Caché de lectura en proceso con TTL e invalidación tras escritura

- **Estado:** Aceptado
- **Fecha:** noviembre de 2026
- **Aspecto relacionado:** Rendimiento / Costo
- **Origen:** Evidencia S12 y S14; `docs/datos/consistencia.md`

## Contexto

Cada búsqueda lee la colección completa de `documentos` en Firestore y filtra en
`busqueda.service`. Con el plan Spark (50 000 lecturas diarias) y 5 documentos de ejemplo, eso
permite ~10 000 búsquedas/día; con 500 documentos, solo 100. La medición de S10 mostró **1 lectura
por búsqueda** sin caché. El cuello de botella es el costo y la latencia de la lectura, no el
filtrado.

La caché no puede ser un TTL ciego: después de publicar un documento, la siguiente búsqueda debe
verlo (si no, el usuario publica y «no aparece»). La ficha S12 pide exactamente una política de
invalidación tras escritura.

## Decisión

1. Una caché **en memoria del proceso** (no Redis, no CDN) guarda la lista pública de documentos
   en `_CacheDocumentos` (`app/documentos/repository.py`).
2. TTL por defecto **60 s**, configurable con `SHAREU_CACHE_TTL_SEGUNDOS`; `0` la apaga.
3. **Invalidación explícita** al final de `crear_documento`, antes de responder: la siguiente
   búsqueda en esa instancia vuelve a leer Firestore y ve el documento nuevo.
4. El TTL es solo la red de seguridad para cambios hechos **por fuera** del proceso (consola de
   Firebase u otra instancia). La consistencia entre instancias es **eventual, acotada por el
   TTL**.
5. Cada lectura devuelve copias (`dict(documento)`), para que `busqueda.service` no mute la lista
   compartida.
6. Se exponen hits, misses, invalidaciones, TTL y entradas en `GET /documentos/cache` y
   `GET /administracion/cache`.

## Opciones evaluadas

### A. Sin caché — descartada
- Ventaja: consistencia fuerte y cero código.
- Desventaja: 1 lectura por búsqueda; con 500 documentos se agota la cuota gratuita con 100
  búsquedas diarias. La medición de S10 es la línea base que motiva el cambio.

### B. Redis gestionado — descartada
- Ventaja: caché compartida entre instancias e invalidación distribuida.
- Desventaja: un servicio más, otra credencial y otro modo de fallo; los planes gratuitos suelen
  exigir tarjeta. Para un solo contenedor de 256 MB es infraestructura desproporcionada.

### C. Caché HTTP (`Cache-Control` en la respuesta) — descartada
- Ventaja: descarga el trabajo al navegador o a un proxy.
- Desventaja: no controla el costo de Firestore desde el servidor y complica la invalidación tras
  publicar; el cliente podría ver resultados viejos sin que la API lo sepa.

### D. Caché en proceso con TTL + invalidación — elegida
- Ventaja: elimina la lectura repetida en el caso normal; una escritura local se ve de inmediato;
  se mide y se expone.
- Desventaja: cada instancia tiene su propia copia y no hay *single-flight*: varias solicitudes
  concurrentes con la caché fría pueden leer Firestore a la vez. La medición de S14 lo cuantifica
  (21 lecturas en 300 búsquedas, 0,07 por búsqueda, por debajo del umbral 0,1).

## Consecuencias

### Positivas
- Lecturas por búsqueda medidas: **1,0 sin caché → 0,07 con caché** (S10 vs. S14).
- El costo de Firestore deja de crecer linealmente con cada búsqueda.
- La invalidación es explícita y está cubierta por `tests/test_cache.py` y
  `tests/test_idempotencia.py::test_la_publicacion_queda_visible_en_la_busqueda`.

### Negativas
- **Ventana de inconsistencia entre instancias:** hasta el TTL (60 s). Se acepta porque el
  despliegue actual tiene una sola instancia y la publicación no es un flujo multiusuario
  concurrente.
- **Stampede en frío:** sin *single-flight*, N solicitudes simultáneas pueden generar N lecturas.
  Aceptado y medido; si el volumen crece, se añade un lock de carga o una caché compartida.
- La memoria de la caché crece con el catálogo completo. Con 256 MB y cientos de documentos es
  aceptable; con decenas de miles habría que paginar o cambiar de estrategia.

## Criterio de reapertura

Reabrir si (a) el despliegue pasa a varias réplicas, (b) el TTL de 60 s produce quejas de
«publiqué y no aparece», o (c) el catálogo deja de caber con holgura en memoria.

## Trazabilidad

`docs/aspectos.md` (A2) → este ADR → `app/documentos/repository.py` (`_CacheDocumentos`,
`crear_documento`, `invalidar_cache`) → `tests/test_cache.py`,
`tests/test_idempotencia.py::test_la_publicacion_queda_visible_en_la_busqueda` →
`docs/evidencia/mediciones/s10-linea-base-sin-cache.*`, `s14-local-asgi.*` → arc42 §8.7.
