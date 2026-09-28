# Estimación de costo mensual — ShareU

## Restricción de partida

El equipo trabaja bajo la restricción de **costo cero y sin tarjeta de
crédito** (ver `docs/arc42/arc42.md` sección 2). Toda pieza de
infraestructura se eligió, en primer lugar, por cumplir esa restricción
(ver ADR 0006 y ADR 0007); esta estimación existe para saber en qué punto
un plan gratuito deja de alcanzar, no para justificar un gasto ya decidido.

## Supuesto de volumen

Volumen esperado durante el semestre (demo de clase + sustentaciones), no
tráfico de producción real:

| Variable | Supuesto |
|---|---|
| Usuarios activos simultáneos en la demo | 5–10 (compañeros y docente) |
| Solicitudes de búsqueda por sustentación | ~50 |
| Frecuencia de despliegue | 1–3 veces por semana (cada push relevante) |
| Horas/mes con tráfico real | < 5 horas (el resto, el backend "duerme" en Render Free) |

## Costo por pieza

| Pieza | Proveedor / plan | Costo mensual | Qué cubre la capa gratuita | Dónde se rompe |
|---|---|---|---|---|
| Backend (FastAPI, contenedor Docker) | Render, plan Free | $0 | 750 horas/mes de cómputo compartidas entre servicios, sin necesidad de tarjeta | Se rompe si se necesita que el servicio nunca "duerma" (requiere plan pago ≈ USD 7/mes), o si se agotan las 750 horas compartidas entre varios servicios del equipo |
| Frontend (Next.js) | Vercel, plan Hobby | $0 | 100 GB de ancho de banda/mes, builds ilimitados para uso no comercial | Se rompe con tráfico sostenido de producción o si el proyecto pasa a uso comercial (Vercel exige plan Pro) |
| Base de datos | SQLite embebido en el contenedor del backend | $0 | Sin límite de "capa gratuita" porque no es un servicio aparte; la limitación es la falta de disco persistente en Render Free (ver ADR 0006) | Se rompe (deja de ser aceptable) si el curso exige persistencia real entre despliegues; ahí habría que sumar un Postgres gestionado gratuito (p. ej. Neon: 0.5 GB, se rompe al superar ese tamaño o el límite de cómputo del free tier) |
| CI (GitHub Actions) | GitHub, plan gratuito de repos públicos | $0 | Minutos ilimitados en repositorios públicos | No aplica mientras el repositorio siga público |
| Análisis de calidad | SonarCloud, plan gratuito para proyectos públicos | $0 | Análisis ilimitado en repositorios públicos | Se rompe si el repositorio pasa a privado (SonarCloud gratuito exige público) |

## Costo total estimado

**USD 0/mes** con el volumen supuesto arriba, sin tarjeta de crédito en
ningún proveedor, siempre que:

1. El repositorio se mantenga público (condición de SonarCloud y GitHub
   Actions gratuitos).
2. El tráfico no obligue a mantener el backend despierto de forma
   continua (Render Free duerme tras inactividad).
3. No se requiera persistencia de datos entre reinicios del backend.

## Punto de ruptura más probable

El punto más probable de ruptura no es de tráfico sino de **persistencia**:
en cuanto el curso o el equipo decidan que los datos deben sobrevivir a un
redeploy (por ejemplo, para demostrar calificaciones reales de usuarios en
`app/calificaciones`), hay que sumar un Postgres gestionado gratuito, lo
que exige reabrir ADR 0006 y migrar `documentos/repository.py`.
