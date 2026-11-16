# Resultado de medición — local-asgi

- **Fecha (UTC):** 2026-11-16T22:52:59.302346+00:00
- **Entorno:** asgi-en-proceso (Firestore falso, sin red)
- **Caché:** encendida (TTL 300 s, invalidada por repetición)
- **Commit:** `local`
- **Carga:** 100 peticiones por repetición,
  3 repeticiones, 10 concurrentes,
  20 de calentamiento.
- **Endpoint:** `GET /busqueda/documentos?materia=Programación`

| Repetición | p50 (ms) | p95 (ms) | p99 (ms) | Errores | Lecturas Firestore |
|---:|---:|---:|---:|---:|---:|
| 1 | 47.69 | 67.54 | 76.56 | 0 | 1 |
| 2 | 55.86 | 68.04 | 84.15 | 0 | 10 |
| 3 | 51.65 | 64.29 | 77.01 | 0 | 10 |

## Resultado agregado

| Métrica | Valor | Umbral |
|---|---:|---|
| p50 | 52.17 ms | — |
| p95 | 67.54 ms | ≤ 500.0 ms |
| p99 | 79.5 ms | — |
| Media | 51.49 ms | — |
| Tasa de error | 0.00 % | < 1 % |
| Throughput | 188.02 req/s | — |
| Lecturas Firestore por búsqueda | 0.07 | ≤ 0.1 con caché |

**Conclusión: cumple.**
