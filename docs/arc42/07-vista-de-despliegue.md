# 7. Vista de despliegue

## 7.1 Entorno real: servidor del laboratorio con Dokploy

| Caja | Dónde se ejecuta | Tecnología | Expuesto en |
|---|---|---|---|
| `api` | Contenedor Docker en el servidor del laboratorio (Dokploy) | Python 3.11 + FastAPI + Uvicorn; imagen `Dockerfile` | `https://api-shareu.iscoutb.dev` (puerto interno 8000) |
| `web` | Contenedor Docker en el mismo servidor | Next.js; imagen `app/frontend/Dockerfile` | `https://shareu.iscoutb.dev` (puerto interno 3000) |
| Firestore | Google Cloud (externo) | Firestore, plan Spark | No expuesto; solo la cuenta de servicio |
| CI/CD | GitHub Actions | `pytest`, contrato, dependencias, medición, SonarCloud condicional | `.github/workflows/tests.yml` |
| Descriptor de despliegue | `Dockploy/compose.lab.yml` | Docker Compose sin `ports`, sin bind mounts, con límites y healthchecks | Dokploy |

```text
GitHub (push a master)
   |
   +--> GitHub Actions: pytest + contrato + pip-audit + npm audit + medición
   |
   +--> Dokploy: docker compose -f Dockploy/compose.lab.yml up -d --build
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

| URL | Estado al 2026-11-16 | Qué se afirma |
|---|---|---|
| `https://shareu.iscoutb.dev` | HTTP 404 | **No verificado**: el despliegue no se presenta como activo |
| `https://api-shareu.iscoutb.dev` | HTTP 404 | **No verificado**: `/health` no se pudo comprobar desde una red externa |

El repositorio contiene el descriptor y las instrucciones, pero **no** una captura o un enlace que
demuestre que el servicio responde. La verificación es una acción humana pendiente: desplegar en
Dokploy, comprobar `/health` y las dos URLs, y actualizar esta tabla y el README con el resultado.
Las mediciones de rendimiento se hicieron en local/ASGI (`docs/evidencia/mediciones/`) y no se
extrapolan al servidor.

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
