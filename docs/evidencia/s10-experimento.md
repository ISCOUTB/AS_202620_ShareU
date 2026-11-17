# S10 — Experimento de rendimiento y costo de lecturas (informe)

## 1. Pregunta e hipótesis

**Pregunta:** ¿la búsqueda de ShareU responde dentro de un umbral perceptible y con un costo de
lecturas aceptable para el plan gratuito de Firestore?

**Hipótesis:** con la caché de lectura encendida, la búsqueda `GET
/busqueda/documentos?materia=Programación` mantiene **p95 ≤ 500 ms**, **tasa de error < 1 %** y
**≤ 0,1 lecturas a Firestore por búsqueda**. Sin caché, la latencia sigue siendo aceptable pero el
costo de lecturas sube a ~1 por búsqueda.

El indicador anterior («≤ 3 interacciones») se conserva como prueba funcional de usabilidad, pero
no sirve como medida del sistema: no distingue una búsqueda lenta de una rápida ni se puede
contrastar con un umbral de costo (ADR 0016).

## 2. Método

- Herramienta versionada: `scripts/medicion/bench_busqueda.py`.
- Carga: 300 solicitudes (3 repeticiones × 100), concurrencia 10, 20 de calentamiento.
- Entorno: **ASGI en proceso** con Firestore falso instrumentado (sin red ni credenciales). Es
  reproducible por un tercero y se ejecuta en CI.
- Línea base: `--sin-cache` fija el TTL en 0. No se cambia código entre corridas.
- Métricas: p50, p95, p99, media, tasa de error, throughput y **lecturas Firestore por búsqueda**
  (contador del Firestore falso).

Comandos:

```bash
python -m scripts.medicion.bench_busqueda --sin-cache --etiqueta linea-base-sin-cache \
  --json-out docs/evidencia/mediciones/s10-linea-base-sin-cache.json \
  --md-out docs/evidencia/mediciones/s10-linea-base-sin-cache.md

python -m scripts.medicion.bench_busqueda --etiqueta local-asgi \
  --json-out docs/evidencia/mediciones/s14-local-asgi.json \
  --md-out docs/evidencia/mediciones/s14-local-asgi.md
```

## 3. Resultados

| Configuración | p95 | Error | Lecturas/búsqueda | Veredicto |
|---|---:|---:|---:|---|
| Línea base (`--sin-cache`) | **72,15 ms** | 0,00 % | **1,00** | Cumple latencia y error; el costo es el esperado sin caché |
| Con caché (S14) | **67,54 ms** | 0,00 % | **0,07** | **Cumple los tres umbrales** |

Detalle por repetición en
[`mediciones/s10-linea-base-sin-cache.md`](mediciones/s10-linea-base-sin-cache.md) y
[`mediciones/s14-local-asgi.md`](mediciones/s14-local-asgi.md). El p95 de la línea base (72 ms) es
ligeramente mayor que el de la corrida con caché (67 ms); la diferencia no es el objetivo del
experimento —el objetivo es el **costo de lecturas**— y en ambos casos está muy por debajo de 500 ms
porque el Firestore falso vive en memoria.

## 4. Lectura honesta de los números

- **La latencia no representa la red.** El modo ASGI no incluye red ni Firestore reales; 67 ms es un
  **límite inferior**. En el servidor del laboratorio la latencia incluirá el viaje a Firestore. Por
  eso el umbral de 500 ms es deliberadamente holgado y la corrida `--url` queda pendiente mientras
  el despliegue responda 404.
- **La métrica que sí cambia es el costo:** 1,00 → 0,07 lecturas por búsqueda. Es una reducción de
  ~14× que sí se traslada al plan gratuito de Firestore, porque cuenta lecturas reales.
- **La caché fría tiene *stampede*:** 21 lecturas en 300 búsquedas (no 3). Diez solicitudes
  concurrentes con la caché vacía leen Firestore a la vez. Se acepta como limitación; la solución
  sería *single-flight*.
- **No se mide el frontend.** El tiempo de render y la percepción del estudiante no están en esta
  corrida.

## 5. Conclusión

La hipótesis se cumple **en el entorno medido**, con los límites declarados. El experimento es
repetible, la línea base se obtiene sin tocar el código y la evidencia queda en JSON y Markdown. La
afirmación que **no** se hace: «el servicio desplegado responde en 67 ms». Esa afirmación requiere
una corrida `--url` contra el servidor, que aún no está verificado.

## 6. Trazabilidad

[ADR 0016](../adr/0016-medicion-de-latencia-y-costo-de-lecturas.md) → `scripts/medicion/bench_busqueda.py`
→ `docs/evidencia/mediciones/s10-*` → este informe → arc42 §10 → `docs/aspectos.md` (A2, A8).
