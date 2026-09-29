# 7. Vista de despliegue

## 7.1 Entorno de producción (dos piezas independientes)

| Caja | Dónde se ejecuta | Tecnología | Expuesto en |
|---|---|---|---|
| Backend ShareU | Render, plan Free, contenedor Docker (`Dockerfile`) | Python 3.11 + FastAPI + Uvicorn | `https://shareu-backend.onrender.com` (URL real: ver README) |
| Frontend ShareU | Vercel, plan Hobby | Next.js (Node.js, build estático + SSR mínimo) | `https://shareu-frontend.vercel.app` (URL real: ver README) |
| Base de datos | Dentro del contenedor del backend (mismo proceso/filesystem) | SQLite, sin disco persistente en el plan Free | No expuesta directamente; solo accesible vía la API del backend |
| CI/CD | GitHub Actions | `pytest` + análisis SonarCloud | `.github/workflows/tests.yml` |

```text
GitHub (push a master)
    |
    +--> GitHub Actions: pytest + prueba de contrato + SonarCloud
    |
    +--> Render (Blueprint render.yaml): build de Dockerfile --> backend en producción
    |
    +--> Vercel (integración Git nativa): build de /frontend --> frontend en producción

Navegador del estudiante
    |
    v
Frontend (Vercel, Next.js)
    |  fetch a NEXT_PUBLIC_API_URL
    v
Backend (Render, FastAPI)
    |
    v
SQLite (filesystem del contenedor, no persistente en plan Free)
```

## 7.2 Justificación de plataforma

Cada pieza de infraestructura tiene su propio ADR con alternativa
descartada, según pide la ficha S8:

- Backend → [`docs/adr/0006-plataforma-backend-despliegue.md`](../adr/0006-plataforma-backend-despliegue.md)
- Frontend → [`docs/adr/0007-plataforma-frontend-despliegue.md`](../adr/0007-plataforma-frontend-despliegue.md)
- Migración de stack de frontend → [`docs/adr/0005-migracion-frontend-nextjs.md`](../adr/0005-migracion-frontend-nextjs.md)

## 7.3 Observabilidad

- **Health check:** `GET /health` en el backend, usado tanto por Docker
  (`HEALTHCHECK`) como por Render para reiniciar el servicio si deja de
  responder.
- **Logs estructurados:** cada solicitud HTTP se registra como una línea
  JSON (`app/main.py`, middleware `registrar_solicitud`) con
  `request_id`, `method`, `path`, `status_code` y `duration_ms`.
- **Métrica ligada a un escenario:** `GET /administracion/metricas`
  expone `total_busquedas` y `tasa_busquedas_sin_resultados`, ligada al
  escenario de usabilidad de `docs/aspectos/aspectos.md` (una búsqueda sin
  resultados obliga a una interacción adicional, erosionando el
  presupuesto de "3 interacciones o menos").

## 7.4 Costo

Ver [`docs/costos/estimacion-costo.md`](../costos/estimacion-costo.md):
estimado en USD 0/mes bajo el volumen supuesto, sin tarjeta de crédito en
ningún proveedor.
