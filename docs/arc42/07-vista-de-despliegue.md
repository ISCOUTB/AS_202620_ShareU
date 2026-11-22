# 7. Vista de despliegue

## 7.1 Entorno real: servidor del laboratorio con Dokploy

| Caja | Dónde se ejecuta | Tecnología | Expuesto en |
|---|---|---|---|
| `api` | Contenedor Docker en el servidor del laboratorio (Dokploy) | Python 3.11 + FastAPI + Uvicorn; imagen `Dockerfile` | `https://api-shareu.iscoutb.dev` (puerto interno 8000) |
| `web` | Contenedor Docker en el mismo servidor | Next.js; imagen `app/frontend/Dockerfile` | `https://shareu.iscoutb.dev` (puerto interno 3000) |
| Firestore | Google Cloud (externo) | Firestore, plan Spark | No expuesto; solo la cuenta de servicio |
| CI/CD | GitHub Actions | `pytest`, contrato, dependencias, medición, SonarCloud condicional | `.github/workflows/tests.yml` |
| Descriptor de despliegue | `Dockploy/compose.lab.yaml` | Docker Compose sin `ports`, sin bind mounts, con límites y healthchecks | Dokploy |

```text
GitHub (push a master)
   |
   +--> GitHub Actions: pytest + contrato + pip-audit + npm audit + medición
   |
   +--> Dokploy: docker compose -f Dockploy/compose.lab.yaml up -d --build
            |
            +--> contenedor api  ---gRPC/HTTPS---> Firestore (externo)
            +--> contenedor web  ---JSON/HTTPS---> api
                     ^
                     |
             Navegador del estudiante (HTTPS, Dokploy/Traefik)
```

## 7.2 Reglas del descriptor

- Sin `ports:`: Dokploy publica por su proxy y los servicios se hablan por la red interna.
- Sin `container_name:` ni bind mounts: despliegue reproducible y sin estado local.
- Límites: `api` 0,5 CPU / 256 MB; `web` 0,5 CPU / 192 MB.
- Healthchecks: `api` consulta `/health`; `web` consulta `/` y espera a que `api` esté sana.
- Secretos solo en Dokploy → Environment: `FIREBASE_CREDENTIALS_JSON` y `SHAREU_ADMIN_TOKEN`.
- CORS del backend fijado a `https://shareu.iscoutb.dev`.

## 7.3 Estado de verificación (honesto)

Comprobación con `curl` el **2026-11-21T22:19:51Z**:

| URL | Estado | Qué se afirma |
|---|---|---|
| `https://shareu.iscoutb.dev` | HTTP **200** | Interfaz Next.js servida; título «ShareU — material académico compartido» |
| `https://api-shareu.iscoutb.dev/health` | HTTP **200** | `{"estado":"ok"}`, `X-Request-Id: c06483a8-f901-42fc-9cbf-e7d17baf44a7` |
| `https://api-shareu.iscoutb.dev/busqueda/documentos` | HTTP **500** | La instancia no tiene credenciales de Firestore; **no** se presenta como flujo verificado |
| `https://api-shareu.iscoutb.dev/administracion/revision` | HTTP **503** | Fail-closed por falta de `SHAREU_ADMIN_TOKEN` |

Los cinco `/ping` de módulo responden 200 y una ruta inexistente devuelve 404. Lo que falta es
**configuración**, no código: cargar `FIREBASE_CREDENTIALS_JSON` y `SHAREU_ADMIN_TOKEN` en Dokploy,
redesplegar el 503 de búsqueda y repetir esta tabla. Las mediciones de rendimiento se hicieron en
local/ASGI (`docs/evidencia/mediciones/`) y no se extrapolan al servidor.

## 7.4 Entorno local

```bash
docker compose up --build      # API en :8000, web en :3000, Firestore externo
```

Sin `FIREBASE_CREDENTIALS_JSON`, la API arranca y `/health` responde, pero las rutas de datos
devuelven 503. Es el comportamiento fail-closed esperado.

## 7.5 Por qué no Render/Vercel

Se evaluaron y descartaron en ADR 0006 y ADR 0007: el plan gratuito de Render duerme y no ofrece
disco persistente, y Vercel Hobby no cubre uso comercial. El laboratorio con Dokploy cumple la
restricción de costo y da control sobre contenedores y dominios. No queda configuración de Render o
Vercel en el repositorio para no mantener un despliegue que no se usa.

## 7.6 Observabilidad del despliegue

- `GET /health` para el healthcheck del contenedor y para una comprobación externa.
- Logs JSON a `stdout` (los recoge Docker/Dokploy): `request_id`, método, ruta, estado, duración y
  campos del evento.
- `GET /administracion/eventos` y `/administracion/cache` para ver el estado de los mecanismos en
  proceso; `GET /administracion/metricas` para la señal de usabilidad.
- CI publica el reporte JUnit y el JSON de la medición como artefactos.
