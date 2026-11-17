# Entrega S10 — resumen de dos páginas

## Página 1: qué se midió y por qué

**Problema.** El indicador de usabilidad «≤ 3 interacciones» no servía como medida del sistema: no
distingue una búsqueda lenta de una rápida, no tiene línea base reproducible y no se puede comparar
con un umbral de costo. El revisor de S10 lo señaló y el equipo lo reemplazó por una medida
operacional (ADR 0016).

**Hipótesis.** Con caché, `GET /busqueda/documentos?materia=Programación` mantiene p95 ≤ 500 ms,
error < 1 % y ≤ 0,1 lecturas Firestore por búsqueda. Sin caché, la latencia sigue siendo aceptable
pero el costo de lecturas sube a ~1 por búsqueda.

**Método.** `scripts/medicion/bench_busqueda.py`, 300 solicitudes (3 × 100), concurrencia 10, 20 de
calentamiento, entorno ASGI en proceso con Firestore falso instrumentado. La línea base se obtiene
con `--sin-cache`, sin cambiar el código. Se miden p50/p95/p99, error, throughput y lecturas por
búsqueda. Cada corrida deja JSON y Markdown en `docs/evidencia/mediciones/`.

## Página 2: resultado y límites

| Configuración | p95 | Error | Lecturas/búsqueda | Veredicto |
|---|---:|---:|---:|---|
| Sin caché (línea base) | 72,15 ms | 0,00 % | 1,00 | Cumple latencia y error |
| Con caché | 67,54 ms | 0,00 % | 0,07 | **Cumple los tres umbrales** |

**Lectura.** La diferencia de latencia es pequeña porque el Firestore falso vive en memoria; lo que
cambia de verdad es el **costo**: ~14× menos lecturas, que es lo que castiga el plan gratuito. El
resultado es reproducible por un tercero y CI puede ejecutarlo sin credenciales.

**Límites que se declaran:**

1. El modo ASGI no incluye red ni Firestore reales: 67 ms es un **límite inferior**, no una promesa
   de producción.
2. El despliegue respondía **404** al 2026-11-16; no se hizo corrida `--url` ni se inventa.
3. La caché fría concurrente produce lecturas extra (*stampede*): 21 en 300 búsquedas. Se acepta;
   la mejora sería *single-flight*.
4. No se mide el frontend ni la percepción del estudiante; la prueba de ≤ 3 interacciones se
   conserva como evidencia funcional separada.

**Conclusión defendible.** «La búsqueda cumple p95, tasa de error y lecturas por búsqueda en una
corrida local reproducible; el servicio desplegado está pendiente de verificación.» Es una
afirmación más útil que un «cumple» sin condiciones.

**Enlaces.** [`s10-experimento.md`](../evidencia/s10-experimento.md),
[`s10-linea-base-sin-cache.md`](../evidencia/mediciones/s10-linea-base-sin-cache.md),
[`s14-local-asgi.md`](../evidencia/mediciones/s14-local-asgi.md), ADR 0016, arc42 §10.
