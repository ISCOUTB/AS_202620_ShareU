# Resultado de medición — linea-base-sin-cache

- **Fecha (UTC):** 2026-11-16T22:53:11.027436+00:00
- **Entorno:** asgi-en-proceso (Firestore falso, sin red)
- **Caché:** apagada (TTL 0)
- **Commit:** `local`
- **Carga:** 100 peticiones por repetición,
  3 repeticiones, 10 concurrentes,
  20 de calentamiento.
- **Endpoint:** `GET /busqueda/documentos?materia=Programación`

| Repetición | p50 (ms) | p95 (ms) | p99 (ms) | Errores | Lecturas Firestore |
|---:|---:|---:|---:|---:|---:|
| 1 | 51.14 | 63.42 | 67.72 | 0 | 100 |
| 2 | 60.08 | 71.41 | 80.63 | 0 | 100 |
| 3 | 57.95 | 73.8 | 79.03 | 0 | 100 |

## Resultado agregado

| Métrica | Valor | Umbral |
|---|---:|---|
| p50 | 56.29 ms | — |
| p95 | 72.15 ms | ≤ 500.0 ms |
| p99 | 79.95 ms | — |
| Media | 55.14 ms | — |
| Tasa de error | 0.00 % | < 1 % |
| Throughput | 175.99 req/s | — |
| Lecturas Firestore por búsqueda | 1.0 | ≤ 0.1 con caché |

**Conclusión: cumple.**
