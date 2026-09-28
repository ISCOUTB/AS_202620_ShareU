# AS_202620_ShareU

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ISCOUTB_AS_202620_ShareU&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ISCOUTB_AS_202620_ShareU)

ShareU es una plataforma web para compartir y encontrar material académico
organizado por universidad, carrera y materia.

## Problema

Los estudiantes suelen perder tiempo buscando apuntes, ejercicios, talleres,
parciales y otros materiales en diferentes medios.

## Arquitectura

ShareU utiliza un **monolito modular**: un único desplegable organizado por
dominios.

- `usuarios`: registro, autenticación y perfil.
- `documentos`: clasificación y persistencia de material académico.
- `busqueda`: búsqueda, filtros y ordenamiento de resultados.
- `calificaciones`: valoración de documentos.
- `administracion`: reportes y moderación.

La decisión está documentada en
[`docs/adr/0001-estilo-arquitectonico.md`](docs/adr/0001-estilo-arquitectonico.md)
y se relaciona con el escenario de usabilidad de
[`docs/aspectos/aspectos.md`](docs/aspectos/aspectos.md).

## Requisitos

- Python 3.10 o superior y `pip` (backend).
- Node.js 18 o superior (frontend).
- Opcional: Docker, para levantar el backend sin instalar Python.


## Instalación

```bash
git clone https://github.com/ISCOUTB/AS_202620_ShareU.git
cd AS_202620_ShareU
```

Crear y activar un entorno virtual:

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`.

Documentación interactiva: `http://127.0.0.1:8000/docs`.

## Sistema desplegado

| Pieza | URL |
|---|---|
| Frontend (Next.js, Vercel) | <URL Vercel> |
| Backend (FastAPI, Render) | <URL Render> |
| Documentación de la API | <URL Render>/docs |
| Verificación de salud | <URL Render>/health |

El backend gratuito "duerme" tras un periodo sin tráfico, así que la primera
solicitud puede tardar unos segundos. Los datos vuelven a los de ejemplo en
cada reinicio (ver `docs/adr/0006-plataforma-backend-despliegue.md`).

## Ejecución con Docker

```bash
docker compose up --build
```

El backend queda en `http://127.0.0.1:8000`.

## Ejecución del frontend

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

El frontend queda en `http://localhost:3000` y consume el backend indicado en
`NEXT_PUBLIC_API_URL`.

## Variables de entorno

Se declaran en `.env.example` (backend) y `frontend/.env.example`. Los valores
reales se configuran en el panel de Render, en Vercel y en GitHub Actions
Secrets (`SONAR_TOKEN`); nunca se suben al repositorio.

## Observabilidad

- `GET /health`: estado del servicio.
- Logs en JSON por solicitud (`request_id`, `method`, `path`, `status_code`, `duration_ms`).
- `GET /administracion/metricas`: total de búsquedas y tasa de búsquedas sin
  resultados, ligada al escenario de usabilidad de `docs/aspectos/aspectos.md`.

## Contrato de la API

`docs/api/openapi.yaml` es la fuente de verdad; `tests/test_contrato.py`
falla si una respuesta real deja de cumplirlo.

## Corte vertical de búsqueda

El recorrido funcional implementado consulta documentos persistidos en SQLite y
permite combinar los filtros en una sola solicitud:

```text
GET /busqueda/documentos
```

Filtros disponibles:

- `universidad`
- `carrera`
- `materia`
- `tipo`
- `palabra_clave`
- `min_calificacion`

Ejemplo:

```bash
curl "http://127.0.0.1:8000/busqueda/documentos?materia=Programación"
```

La respuesta contiene el total y los resultados con título, universidad,
carrera, materia, tipo, autor y calificación.

## Verificación

Endpoint de salud:

```bash
curl http://127.0.0.1:8000/health
```

Respuesta esperada:

```json
{"estado": "ok"}
```

Los cinco módulos conservan un endpoint de verificación:

- `/usuarios/ping`
- `/documentos/ping`
- `/busqueda/ping`
- `/calificaciones/ping`
- `/administracion/ping`

## Pruebas y medición

```bash
pytest -q
```

El escenario de usabilidad se verifica también mediante una medición reproducible:
una búsqueda con cualquier combinación de criterios se resuelve mediante **una sola
solicitud HTTP** al endpoint `/busqueda/documentos`. El objetivo es mantener el
flujo de búsqueda dentro del umbral de **3 interacciones o menos**. La evidencia
metodológica se encuentra en [`docs/evidencia/medicion-usabilidad.md`](docs/evidencia/medicion-usabilidad.md).

El workflow de GitHub Actions en
[`.github/workflows/tests.yml`](.github/workflows/tests.yml) ejecuta estas
pruebas automáticamente en cada `push` y `pull_request`.

## Documentación

- [arc42](docs/arc42/arc42.md)
- [C4 nivel 1](docs/c4/nivel1.mmd)
- [C4 nivel 2](docs/c4/nivel-2.md) — [diagrama editable](docs/c4/nivel2.mmd)
- [ADR 0001](docs/adr/0001-estilo-arquitectonico.md)
- [Aspectos de calidad](docs/aspectos/aspectos.md)
- [Uso de IA](docs/ia/ia.md)
- [ADR 0002](docs/adr/0002-usabilidad-busqueda-en-una-solicitud.md), [0003](docs/adr/0003-separacion-contexto-calificaciones.md), [0004](docs/adr/0004-integracion-sincrona-y-asincrona.md), [0005](docs/adr/0005-migracion-frontend-nextjs.md), [0006](docs/adr/0006-plataforma-backend-despliegue.md), [0007](docs/adr/0007-plataforma-frontend-despliegue.md)
- [Contrato OpenAPI](docs/api/openapi.yaml)
- [Estimación de costo](docs/costos/estimacion-costo.md)
