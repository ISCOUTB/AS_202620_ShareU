# ADR 0006: Desplegar el backend como contenedor Docker en el servidor del laboratorio (Dokploy)

- **Estado:** Aceptado
- **Fecha:** octubre de 2026, revisado en noviembre de 2026
- **Aspecto relacionado:** Disponibilidad / Costo / Operabilidad
- **Reemplaza parcialmente:** la parte de persistencia de esta decisión (SQLite sin disco
  persistente) queda reemplazada por [ADR 0012](0012-persistencia-en-firestore.md)

## Contexto

El backend es un único proceso FastAPI (ADR 0001). La restricción de costo exige **USD 0/mes y
ninguna tarjeta de crédito** (arc42 §2). Además, el curso entrega un servidor de laboratorio con
Dokploy, que ya aplica HTTPS, reinicio y límites de recursos. Se necesita un descriptor versionado
que permita reproducir el despliegue, no solo un panel configurado a mano.

## Decisión

1. El backend se empaqueta con `Dockerfile` (raíz y `Dockploy/Dockerfile.api`) sobre
   `python:3.12-slim`, con usuario sin privilegios y `HEALTHCHECK` contra `/health`.
2. El despliegue de producción se describe en **`Dockploy/compose.lab.yaml`**: dos servicios
   (`api` y `web`), sin puertos publicados, sin bind mounts y con límites de CPU/memoria. Dokploy
   publica `api-shareu.iscoutb.dev` hacia el puerto 8000.
3. La base de datos **no** es un contenedor: es Firestore, un servicio externo (ADR 0012).
4. Los secretos (`FIREBASE_CREDENTIALS_JSON`, `SHAREU_ADMIN_TOKEN`) se configuran en Dokploy →
   Environment y nunca se versionan.
5. `docker-compose.yml` en la raíz sirve para desarrollo local y usa el mismo `Dockerfile`.

## Opciones evaluadas

### A. Render Free — descartada
- Ventaja: integración Git nativa y blueprint sencillo.
- Desventaja: el servicio "duerme" tras inactividad; el primer request tarda decenas de segundos,
  justo el modo de fallo «responde tarde» de S11. Además, el servidor del laboratorio ya está
  disponible y evita depender de otra cuenta.

### B. Railway / Fly.io — descartadas
- Ventaja: despliegue cómodo y regiones.
- Desventaja: Railway exige tarjeta para el plan gratuito; Fly.io cambió sus condiciones y también
  pide tarjeta. Incumplen la restricción de costo.

### C. Servidor del laboratorio con Dokploy — elegida
- Ventaja: costo USD 0, HTTPS y dominio institucional (`*.iscoutb.dev`), sin tarjeta ni cuentas
  nuevas; el descriptor queda en el repositorio.
- Desventaja: el equipo no controla el sistema operativo del servidor; el arranque en frío y los
  límites de 256 MB son del laboratorio, no del proveedor. La disponibilidad depende de una
  máquina compartida.

### D. Ejecutar `uvicorn` directamente en una máquina del equipo — descartada
- Desventaja: no es reproducible, no tiene HTTPS ni reinicio automático y expone el equipo del
  estudiante.

## Consecuencias

### Positivas
- Un solo artefacto (`imagen`) reproducible en local y en el laboratorio.
- El health check permite que Docker y Dokploy reinicien el servicio si deja de responder.
- El costo sigue en USD 0 y el descriptor se puede auditar en el repositorio.

### Negativas
- **Persistencia:** este ADR ya no decide la base de datos; la decisión vigente es Firestore
  (ADR 0012). La parte de SQLite se conserva solo como historia.
- El contenedor tiene 256 MB de memoria: la caché en proceso (ADR 0013) debe ser pequeña y el
  outbox (ADR 0015) no puede crecer sin límite.
- No hay autoescalado; el techo de carga se mide y se declara (S10/S14).

## Estado de verificación del despliegue

El 2026-11-21 se comprobaron `https://shareu.iscoutb.dev` (**HTTP 200**) y
`https://api-shareu.iscoutb.dev/health` (**HTTP 200**); `/busqueda/documentos` responde **500**
porque la instancia no tiene credenciales de Firestore. El descriptor y el dominio están
desplegados; el flujo de datos sigue pendiente de configuración y así se declara. El detalle con
`X-Request-Id` está en el README y en [`docs/arc42/07`](../arc42/07-vista-de-despliegue.md) §7.3.

## Trazabilidad

`docs/aspectos.md` (A3, A8) → este ADR → `Dockerfile`, `Dockploy/Dockerfile.api`,
`Dockploy/compose.lab.yaml` → `tests/test_esqueleto.py` (health) → `docs/arc42/arc42.md` §7.
