# ADR 0016: Medir el escenario de rendimiento con latencia p95 y lecturas por búsqueda

- **Estado:** Aceptado
- **Fecha:** noviembre de 2026
- **Aspecto relacionado:** Rendimiento / Costo
- **Origen:** Evidencia S10 y S14; reemplaza el indicador «≤ 3 interacciones» como métrica del
  reto de S10

## Contexto

En S8 el escenario de usabilidad se medía contando «interacciones» (campos llenados + clic). El
revisor de S10 señaló que ese indicador **no es operacional** para el reto: no distingue una
búsqueda lenta de una rápida y no se puede contrastar con un umbral de sistema. La ficha S10 pide
hipótesis, línea base reproducible, umbral y resultado. La ficha S14 pide medir un atributo de
calidad contra el umbral declarado en arc42 §10.

El atributo que el usuario percibe y que el costo de Firestore castiga es el **tiempo de la
búsqueda** y el **número de lecturas** que consume.

## Decisión

1. El escenario medido es `GET /busqueda/documentos?materia=Programación` con carga concurrente.
2. Umbral declarado en arc42 §10:
   - **p95 ≤ 500 ms**;
   - **tasa de error < 1 %**;
   - con caché encendida, **≤ 0,1 lecturas a Firestore por búsqueda**.
3. Herramienta versionada: `scripts/medicion/bench_busqueda.py` (httpx + transporte ASGI o HTTP),
   con calentamiento, repeticiones, percentiles y contador de lecturas del Firestore falso.
4. La línea base se obtiene **sin cambiar el código**: `--sin-cache` fija el TTL en 0. Así la
   comparación es justa y reproducible.
5. Se declaran dos entornos: `asgi-en-proceso` (Firestore falso, sin red; se puede repetir en CI)
   y `http` (servicio desplegado). El informe dice cuál se usó y qué significa.
6. Cada corrida deja artefactos JSON y Markdown en `docs/evidencia/mediciones/`; CI publica los
   suyos como artefacto.

## Opciones evaluadas

### A. Mantener «≤ 3 interacciones» — descartada
- Ventaja: fácil de contar.
- Desventaja: no mide el sistema, no tiene línea base reproducible y no se puede contrastar con un
  umbral de latencia o costo. El revisor la rechazó como métrica del reto.

### B. Medir solo en producción — descartada como única fuente
- Ventaja: mide la red y Firestore reales.
- Desventaja: el despliegue no está verificado (HTTP 404 al 2026-11-16), el plan gratuito duerme y
  la medición no sería repetible por un tercero. Se conserva como modo `--url` para cuando el
  despliegue esté disponible.

### C. Medir con k6/JMeter/Locust — descartada
- Ventaja: herramientas estándar y reportes ricos.
- Desventaja: otra dependencia y otro lenguaje; el equipo ya tiene Python y httpx, y el contador de
  lecturas de Firestore necesita instrumentación propia. La herramienta propia es más pequeña y
  mide exactamente lo que el umbral exige.

### D. Medición propia ASGI/HTTP con umbral triple — elegida
- Ventaja: reproducible, versionada, sin credenciales en el modo ASGI, y mide latencia, error y
  costo de lecturas en la misma corrida.
- Desventaja: el modo ASGI no incluye red ni Firestore reales; se declara como límite de validez y
  no se extrapola a producción.

## Consecuencias

### Positivas
- Línea base y resultado son comparables: **p95 72,15 ms / 1,0 lectura** sin caché vs
  **p95 67,54 ms / 0,07 lecturas** con caché (S10 y S14).
- El umbral vive en un solo lugar (arc42 §10) y la herramienta lo repite.
- CI puede ejecutar la medición sin credenciales.

### Negativas
- La latencia ASGI no representa la red del laboratorio; el número es un **límite inferior**.
- Sin *single-flight*, la caché fría genera lecturas concurrentes; la corrida de S14 lo muestra
  (21 lecturas en 300 búsquedas) y se acepta como limitación conocida.
- La medición no cubre el frontend ni la percepción del estudiante; el escenario de usabilidad
  conserva su prueba de interacciones como evidencia separada.

## Criterio de reapertura

Reabrir si el despliegue se estabiliza y se puede medir con `--url`, si el umbral cambia (debe
quedar registrado en un ADR nuevo) o si el catálogo crece hasta que el filtrado en memoria deje de
ser el cuello de botella.

## Trazabilidad

`docs/aspectos.md` (A2) → este ADR → `scripts/medicion/bench_busqueda.py` →
`docs/evidencia/mediciones/s10-linea-base-sin-cache.*`, `s14-local-asgi.*` →
`docs/evidencia/s10-experimento.md`, `docs/evidencia/s14-medicion.md` → arc42 §10.
