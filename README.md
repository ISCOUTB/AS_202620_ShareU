# AS_202620_ShareU

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ISCOUTB_AS_202620_ShareU&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ISCOUTB_AS_202620_ShareU)

> El *badge* refleja el estado real del proyecto público en SonarCloud (organización `isco-utb`).
> Al 2026-11-17 el gate está en **ERROR** (`new_reliability_rating=3`, `new_security_rating=3`) por
> 44 incidencias abiertas; no se oculta ni se presenta como verde. El detalle y la condición para
> cerrarlo están en [`docs/arc42/11-riesgos-y-deuda-tecnica.md`](docs/arc42/11-riesgos-y-deuda-tecnica.md) §11.5.

ShareU es una plataforma web para **compartir y encontrar material académico** organizado por
universidad, carrera y materia: apuntes, ejercicios, talleres, parciales y guías.

- **Backend:** Python 3.11+ / FastAPI, monolito modular.
- **Frontend:** Next.js 14 (React).
- **Datos:** Firestore (Firebase, plan Spark).
- **Mensajería:** outbox en proceso para `documento.publicado`.
- **Despliegue:** contenedores Docker en el servidor del laboratorio con Dokploy.
- **Costo:** USD 0/mes bajo el volumen académico (ver puntos de ruptura).

## Arranque rápido

### Con Docker (recomendado)

```bash
copy .env.example .env      # Windows
cp .env.example .env        # Linux/macOS
docker compose up --build
```

- API: <http://127.0.0.1:8000> — documentación en `/docs`, salud en `/health`.
- Frontend: <http://127.0.0.1:3000>.
- Sin `FIREBASE_CREDENTIALS_JSON`, la API arranca y `/health` responde, pero las rutas de datos
  devuelven **503**; es el comportamiento fail-closed esperado.

### Sin Docker

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate       # Linux/macOS
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd app/frontend
copy .env.example .env.local      # o cp
npm install
npm run dev
```

## Configuración

| Variable | Para qué | Si falta |
|---|---|---|
| `FIREBASE_CREDENTIALS_JSON` | Cuenta de servicio de Firebase (JSON en una línea) | Rutas de datos devuelven 503 |
| `SHAREU_ADMIN_TOKEN` | Escritura y bandeja de moderación | Rutas protegidas devuelven 503 |
| `SHAREU_FRONTEND_ORIGIN` | Orígenes CORS separados por coma | Se aceptan los de Next.js en local |
| `SHAREU_CACHE_TTL_SEGUNDOS` | TTL de la caché; `0` la apaga | 60 |
| `SHAREU_EVENTO_ESPERA_BASE_SEGUNDOS` | Base de reintentos del outbox | 1,0 |
| `NEXT_PUBLIC_API_URL` | URL de la API que consume el frontend | `http://127.0.0.1:8000` |

Los valores reales viven en Dokploy → Environment o en un `.env` local. **Nunca** se versionan.
`.env.example` solo contiene marcadores.

## Endpoints principales

| Método y ruta | Qué hace | Credencial |
|---|---|---|
| `GET /health` | Estado del servicio | No |
| `GET /busqueda/documentos` | Búsqueda combinada: `universidad`, `carrera`, `materia`, `tipo`, `palabra_clave`, `min_calificacion` | No |
| `POST /documentos` | Publica metadatos; requiere `Idempotency-Key` | `X-Admin-Token` |
| `GET /documentos/cache` | Estado de la caché | No |
| `GET /administracion/metricas` | Búsquedas y tasa sin resultados | No |
| `GET /administracion/cache` | Caché (vista administrativa) | No |
| `GET /administracion/eventos` | Contadores del outbox | No |
| `GET /administracion/revision` | Bandeja de revisión | `X-Admin-Token` |
| `POST /administracion/revision/{id}/resolver` | Aprueba y retira de la bandeja | `X-Admin-Token` |

Ejemplo de búsqueda:

```bash
curl "http://127.0.0.1:8000/busqueda/documentos?materia=Programación"
```

Ejemplo de publicación idempotente:

```bash
curl -X POST http://127.0.0.1:8000/documentos \
  -H "Content-Type: application/json" \
  -H "X-Admin-Token: $SHAREU_ADMIN_TOKEN" \
  -H "Idempotency-Key: demo-0001" \
  -d '{"titulo":"Taller de Python","universidad":"UTB","carrera":"Ingeniería de Sistemas","materia":"Programación","tipo":"Taller","autor":"Ana","calificacion":4.5,"palabras_clave":"python"}'
```

Repetir con la misma clave y el mismo cuerpo devuelve **200** y no duplica el documento ni el
evento; con otro cuerpo devuelve **409**.

## Pruebas

```bash
pytest -q
```

No requieren credenciales: usan un Firestore falso (`tests/firestore_falso.py`). Cubren contrato,
fronteras, búsqueda, usabilidad, caché, idempotencia, eventos, resiliencia y seguridad. El workflow
[`.github/workflows/tests.yml`](.github/workflows/tests.yml) ejecuta además `pip-audit`, `npm audit`,
la medición y SonarCloud cuando hay token.

## Medición de rendimiento y costo

```bash
python -m scripts.medicion.bench_busqueda --sin-cache --etiqueta linea-base-sin-cache \
  --json-out docs/evidencia/mediciones/s10-linea-base-sin-cache.json \
  --md-out docs/evidencia/mediciones/s10-linea-base-sin-cache.md

python -m scripts.medicion.bench_busqueda --etiqueta local-asgi \
  --json-out docs/evidencia/mediciones/s14-local-asgi.json \
  --md-out docs/evidencia/mediciones/s14-local-asgi.md
```

Umbral (arc42 §10): **p95 ≤ 500 ms**, **error < 1 %**, **≤ 0,1 lecturas Firestore/búsqueda** con
caché. Resultado local: 67,54 ms, 0 % y 0,07 lecturas. La corrida es ASGI en proceso (sin red): es un
límite inferior y no se extrapola al despliegue.

Contra el servicio desplegado, el banco exige permiso explícito para hosts externos (defensa contra
SSRF, S13):

```bash
SHAREU_BENCH_PERMITIR_REMOTO=1 python -m scripts.medicion.bench_busqueda \
  --url https://api-shareu.iscoutb.dev --etiqueta despliegue
```

Los artefactos solo se escriben dentro de `docs/evidencia/mediciones/`; una ruta con `..` o fuera de
esa carpeta se rechaza.

## Estado del despliegue (honesto)

| URL | Estado al 2026-11-16 |
|---|---|
| <https://shareu.iscoutb.dev> | **HTTP 404 — no verificado** |
| <https://api-shareu.iscoutb.dev> | **HTTP 404 — no verificado** |

El descriptor `Dockploy/compose.lab.yml` y los Dockerfile están listos, pero **no** se afirma que el
servicio esté activo. Verificarlo —desplegar, comprobar `/health` y actualizar esta tabla— es una
acción humana pendiente.

## Arquitectura

Monolito modular con cinco dominios (`usuarios`, `documentos`, `busqueda`, `calificaciones`,
`administracion`) y tres mecanismos transversales:

- **Caché de lectura** en proceso con TTL e invalidación tras escribir (ADR 0013).
- **Outbox** en proceso para `documento.publicado`, con deduplicación, reintentos y DLQ (ADR 0015).
- **Seguridad**: `X-Admin-Token` fail-closed, CORS explícito y cabeceras (ADR 0014).

Un módulo no importa archivos internos de otro; el cableado y la suscripción al evento viven en
`app/main.py`. Lo verifica `tests/test_fronteras.py`.

```text
Navegador -> Next.js -> FastAPI -> Firestore
                           |
                           +-> caché
                           +-> outbox -> administración (bandeja)
```

## Documentación

| Documento | Contenido |
|---|---|
| [arc42](docs/arc42/00-portada.md) | Arquitectura completa, §1–§12 |
| [C4 nivel 1](docs/c4/nivel1.mmd) / [nivel 2](docs/c4/nivel-2.md) | Contexto y contenedores ([editable](docs/c4/nivel2.mmd)) |
| [Aspectos y trazabilidad](docs/aspectos.md) | Tabla de 8 columnas: requisito → C4 → ADR → código → pruebas → evidencia |
| [ADR](docs/adr/) | 16 decisiones con alternativas y consecuencias |
| [Contrato OpenAPI](docs/api/openapi.yaml) | Fuente de verdad de la API (v1.3.0) |
| [Consistencia y caché](docs/datos/consistencia.md) | Operación → garantía |
| [Contrato del evento](docs/eventos/contrato-evento.md) / [límites](docs/eventos/limites.md) | Mensajería |
| [Modos de fallo](docs/resiliencia/modos-de-fallo.md) | No responde / tarde / dos veces, idempotencia y saga |
| [Amenazas](docs/seguridad/amenazas.md) / [dependencias](docs/seguridad/dependencias.md) | STRIDE, privacidad y cadena de suministro |
| [Costos](docs/costos/estimacion-costo.md) | USD 0/mes y puntos de ruptura |
| [Evidencia S10–S14](docs/evidencia/) | Informes y mediciones |
| [Resúmenes de entrega](docs/entrega/) | Dos páginas S10 y una página S11–S14 |
| [Uso de IA](docs/ia.md) | Registro por semana con rechazos y revisión |
| [DDD](docs/ddd/contextos.md) | Contextos, propiedad de datos y auditoría |

## Limitaciones conocidas

- No hay autenticación de estudiantes; solo token administrativo (ADR 0014).
- No se almacenan archivos, solo metadatos.
- La caché y el outbox viven en memoria: una instancia, sin durabilidad (ADR 0013/0015).
- No hay *single-flight*: la caché fría concurrente genera lecturas extra.
- Sin rate limit; el límite de CPU/memoria del contenedor es el techo.
- El despliegue y el pipeline remoto no están verificados; se declaran abiertos.

Todas las limitaciones y su criterio de reapertura están en
[arc42 §11](docs/arc42/11-riesgos-y-deuda-tecnica.md).
