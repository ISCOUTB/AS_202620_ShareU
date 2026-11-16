# ADR 0005: Migrar el frontend a Next.js (React) en `app/frontend`

- **Estado:** Aceptado
- **Fecha:** octubre de 2026
- **Aspecto relacionado:** Usabilidad / Mantenibilidad
- **Origen:** Evidencia S8; restricción de stack del curso (Frontend: Flutter o Next.js)

## Contexto

El primer corte entregó una interfaz estática (`index.html` + `script.js`) que consumía la API con
`fetch`. Funcionaba para demostrar el flujo, pero no tenía componentes reutilizables, no validaba
tipos en tiempo de compilación y mezclaba la presentación con la construcción manual del DOM. La
restricción del curso admite Flutter o Next.js; la API ya es HTTP/JSON, de modo que el frontend no
puede acoplarse a la persistencia (ADR 0012).

## Decisión

El frontend canónico vive en `app/frontend/` y se implementa con **Next.js 14 (App Router) +
React 18 + TypeScript**. La comunicación con el backend es exclusivamente `fetch` a
`NEXT_PUBLIC_API_URL` (`app/frontend/lib/api.ts`), con timeout y un reintento (S11). La carpeta
`shareuwensite-main/` es una copia histórica del sitio estático y no se despliega.

## Opciones evaluadas

### A. Mantener HTML/CSS/JS estático — descartada
- Ventaja: cero build, cero dependencias de Node.
- Desventaja: el DOM se manipula a mano, no hay tipos ni componentes, y cada cambio de la interfaz
  obliga a repetir la construcción de filtros y estados de error. El costo de mantener el flujo de
  usabilidad (ADR 0002) crece con cada corte.

### B. Flutter (web) — descartada
- Ventaja: un solo lenguaje para web y móvil, componentes consistentes.
- Desventaja: exige aprender Dart, añade un runtime y un pipeline de build distintos, y el equipo ya
  tenía experiencia en TypeScript. El costo de aprendizaje no se justifica para una sola pantalla.

### C. Next.js 14 con React y TypeScript — elegida
- Ventaja: componentes y tipos; build reproducible con `npm ci`; despliegue como contenedor Node
  (ADR 0007) o en Vercel; la API no cambia.
- Desventaja: aparece una cadena de build Node y una superficie de dependencias que hay que auditar
  (`npm audit`, Dependabot).

## Consecuencias

### Positivas
- El flujo de búsqueda se expresa en un componente con estado explícito (filtros, carga, error y
  resultados), lo que hace verificable el presupuesto de interacciones.
- El contrato HTTP sigue siendo la única frontera: migrar de nuevo el frontend no toca el backend.

### Negativas
- `app/frontend/package-lock.json` debe mantenerse sincronizado; el equipo lo actualizó a
  `next@14.2.35` tras el hallazgo de deprecación de S9.
- Sin runner de pruebas de frontend, los modos de fallo de red se verifican por revisión de código y
  no por prueba automatizada (declarado en `docs/resiliencia/modos-de-fallo.md`).

## Trazabilidad

`docs/aspectos.md` (A1, A7) → este ADR → `app/frontend/app/page.tsx`, `app/frontend/lib/api.ts`,
`app/frontend/package.json` → `docs/c4/nivel-2.md` → `Dockerfile` de `app/frontend`.
