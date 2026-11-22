# ADR 0007: Desplegar el frontend Next.js en el mismo servidor del laboratorio

- **Estado:** Aceptado
- **Fecha:** octubre de 2026, revisado en noviembre de 2026
- **Aspecto relacionado:** Usabilidad / Costo / Operabilidad
- **Relacionado:** [ADR 0005](0005-migracion-frontend-nextjs.md), [ADR 0006](0006-plataforma-backend-despliegue.md)

## Contexto

El frontend es una aplicación Next.js 14 (ADR 0005) que consume la API por `NEXT_PUBLIC_API_URL`.
La restricción de costo y la existencia de un servidor con Dokploy (ADR 0006) abren dos caminos:
publicarlo en el mismo servidor o usar un proveedor de frontend. La decisión debe explicar cómo se
fija la URL de la API en el build y cómo se sirve el resultado.

## Decisión

1. El frontend se construye con `Dockploy/Dockerfile.web` (equivalente en
   `app/frontend/Dockerfile`) y se ejecuta con `next start` en el puerto 3000.
2. Se despliega como servicio `web` en `Dockploy/compose.lab.yaml`, detrás del dominio
   `shareu.iscoutb.dev`, con 192 MB de memoria y health check HTTP.
3. `NEXT_PUBLIC_API_URL=https://api-shareu.iscoutb.dev` se pasa como **build arg**: Next.js
   incrusta las variables `NEXT_PUBLIC_*` en el bundle, así que cambiarla exige reconstruir la
   imagen (no basta reiniciar).
4. El CORS del backend permite exactamente `https://shareu.iscoutb.dev`
   (`SHAREU_FRONTEND_ORIGIN`), no `*`.

## Opciones evaluadas

### A. Vercel Hobby — descartada
- Ventaja: despliegue Git nativo, CDN y previews.
- Desventaja: obliga a mantener dos paneles y dos configuraciones de variables; el equipo ya tiene
  un servidor con HTTPS y el despliegue conjunto reduce piezas. Vercel sigue siendo una alternativa
  válida si el laboratorio deja de estar disponible.

### B. Exportación estática (`output: "export"`) servida por Nginx — descartada
- Ventaja: imagen más pequeña y sin proceso Node.
- Desventaja: limita las capacidades de Next.js y separa el build del servidor; no aporta nada al
  flujo actual, que es una sola página que llama a la API.

### C. Contenedor Next.js en el servidor del laboratorio — elegida
- Ventaja: una sola plataforma, un solo `docker compose`, mismo dominio institucional y costo USD 0.
- Desventaja: el frontend compite por CPU/memoria con la API en la misma máquina; un fallo del
  servidor tumba ambas piezas.

## Consecuencias

### Positivas
- El despliegue completo se reproduce con un comando y un archivo de variables.
- El frontend no conoce Firebase: solo habla con la API (ADR 0012).

### Negativas
- Cambiar la URL de la API exige reconstruir la imagen del frontend; está documentado para evitar
  el error de «cambié la variable y no surtió efecto».
- Sin CDN, la latencia del frontend depende del servidor del laboratorio. La medición de S14 se
  hace contra la API, no contra el frontend, y así se declara.

## Estado de verificación

El 2026-11-21 `https://shareu.iscoutb.dev` respondió **HTTP 200** y sirve la interfaz Next.js. El
flujo de datos de la API está declarado como pendiente en [`docs/arc42/07`](../arc42/07-vista-de-despliegue.md)
§7.3 porque la búsqueda responde 500 por falta de credenciales de Firestore.

## Trazabilidad

`docs/aspectos.md` (A1, A7, A8) → este ADR → `Dockploy/Dockerfile.web`,
`app/frontend/Dockerfile`, `Dockploy/compose.lab.yaml` → `docs/c4/nivel-2.md` → README.
