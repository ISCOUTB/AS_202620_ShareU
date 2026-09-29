date: agosto 2026
title: "Documentación de arquitectura ShareU — arc42"
---

# 1. Introducción y objetivos

## 1.1 Descripción

ShareU es una plataforma web para compartir y encontrar material académico
organizado por universidad, carrera y materia. Busca reducir el tiempo que los
estudiantes emplean buscando apuntes, ejercicios, talleres, parciales y otros
recursos dispersos en distintos medios.

## 1.2 Objetivos de calidad

| Objetivo | Prioridad | Indicador |
|---|---|---|
| Usabilidad | Muy alta | Encontrar material relevante en menos de 3 interacciones |
| Seguridad | Alta | Acceso controlado según rol |
| Rendimiento | Alta | Búsquedas con filtros respondidas sin pasos innecesarios |
| Disponibilidad | Alta | API operativa y verificable mediante `/health` |
| Mantenibilidad | Media | Cambios localizados dentro de módulos |
| Escalabilidad | Media | Posibilidad de extraer un módulo si la evidencia lo justifica |

El escenario de usabilidad completo está en
[`../aspectos/aspectos.md`](../aspectos/aspectos.md).

# 2. Restricciones arquitectónicas

- El backend se implementa inicialmente con Python y FastAPI.
- El frontend se implementa con Next.js (ver ADR 0005), cumpliendo la
  restricción de stack del curso (Backend: NestJS/FastAPI — Frontend:
  Flutter/Next.js).
- El proyecto se entrega incrementalmente.
- El despliegue inicial es de dos servicios independientes: backend
  (Render) y frontend (Vercel) — ver ADR 0006 y ADR 0007.
- Los cinco dominios deben conservar fronteras explícitas.
- La persistencia del corte vertical utiliza SQLite y la biblioteca estándar
  de Python para mantener el alcance pequeño.
- Las pruebas se ejecutan con `pytest`, incluida una prueba de contrato
  sobre `docs/api/openapi.yaml` (ver ADR y ficha S7).
- La integración continua se realiza con GitHub Actions.
- Las decisiones arquitectónicas se registran mediante ADR.
- Toda API pública se especifica primero como contrato ejecutable
  (OpenAPI/AsyncAPI) versionado en `docs/api/`, y ese contrato se verifica
  con una prueba de contrato en el pipeline.
- **Restricción de costo:** el despliegue debe mantenerse en **USD 0/mes**
  y **sin tarjeta de crédito** en ningún proveedor, mientras el proyecto
  sea un ejercicio académico (ver `docs/costos/estimacion-costo.md`). Esta
  restricción es la que descarta alternativas como Railway en ADR 0006.

# 3. Contexto y alcance

## 3.1 Contexto de negocio

| Actor | Interacción con ShareU |
|---|---|
| Estudiante | Busca, consulta, comparte y califica material académico |
| Administrador | Gestiona usuarios, documentos y reportes |
| Servicio de almacenamiento | Guarda y recupera archivos académicos |
| Servicio de correo | Envía notificaciones transaccionales |

## 3.2 Contexto técnico

En la implementación actual el backend es una aplicación FastAPI que contiene
los cinco módulos de dominio. La base de datos SQLite persiste los metadatos
utilizados por el corte vertical de búsqueda.

```text
Estudiante / Administrador
          |
       HTTPS
          v
   Aplicación web
          |
       JSON/HTTP
          v
    API FastAPI
          |
   +------+------+------+------+------+
   |      |      |      |      |      |
Usuarios Docs  Búsqueda Calificaciones Administración
                 |
                 v
               SQLite
```

# 4. Estrategia de solución

La estrategia es un **monolito modular**. El sistema tiene un único
desplegable, pero cada dominio mantiene una responsabilidad y una frontera
explícita.

La comparación de alternativas está en
[`../aspectos/aspectos.md`](../aspectos/aspectos.md). La decisión arquitectónica
base está en [`../adr/0001-estilo-arquitectonico.md`](../adr/0001-estilo-arquitectonico.md)
y la decisión específica del flujo de búsqueda en
[`../adr/0002-usabilidad-busqueda-en-una-solicitud.md`](../adr/0002-usabilidad-busqueda-en-una-solicitud.md).

## Módulos

- **usuarios:** registro, autenticación y perfiles.
- **documentos:** clasificación y persistencia de documentos.
- **busqueda:** filtros y ordenamiento de resultados.
- **calificaciones:** valoración de documentos.
- **administracion:** reportes y moderación.

La regla principal es que un módulo no accede directamente a la persistencia
interna de otro. Cuando necesita información, utiliza la interfaz de servicio
pública del módulo correspondiente.

# 5. Vista de bloques de construcción

## 5.1 Sistema completo

```text
app.main
  |
  +--> usuarios.router
  +--> documentos.router --> documentos.service --> documentos.repository --> SQLite
  +--> busqueda.router --> busqueda.service --> documentos.service
                                              +--> administracion.service (métrica, ADR 0008)
  +--> calificaciones.router
  +--> administracion.router
```

`app/main.py` es el punto de composición de los routers. No contiene lógica de
dominio.

## 5.2 Responsabilidades

| Bloque | Responsabilidad | Ubicación |
|---|---|---|
| Usuarios | Usuarios y autenticación | `app/usuarios/` |
| Documentos | Metadatos y persistencia de documentos | `app/documentos/` |
| Búsqueda | Filtrado, palabra clave y ranking | `app/busqueda/` |
| Calificaciones | Valoraciones | `app/calificaciones/` |
| Administración | Reportes y moderación | `app/administracion/` |

## 5.3 Corte vertical de la semana 4

La funcionalidad implementada atraviesa API, lógica de dominio y persistencia:

```text
GET /busqueda/documentos?materia=Programación
        |
        v
busqueda.router
        |
        v
busqueda.service
        |
        v
documentos.service
        |
        v
documentos.repository
        |
        v
SQLite
```

La búsqueda soporta universidad, carrera, materia, tipo, palabra clave y
calificación mínima. El resultado se ordena por calificación descendente.

# 6. Vista de ejecución

## 6.1 Escenario: buscar material (síncrono)

Contrato: [`docs/api/openapi.yaml`](../api/openapi.yaml) — `GET
/busqueda/documentos`. Integración síncrona de extremo a extremo: el
estudiante espera la respuesta HTTP para ver resultados (justificación de
por qué es síncrona, y no asíncrona, en
[`../adr/0004-integracion-sincrona-y-asincrona.md`](../adr/0004-integracion-sincrona-y-asincrona.md)).

| Paso | De → a | Protocolo / formato | Naturaleza |
|---|---|---|---|
| 1 | Estudiante → Aplicación web | HTTPS | Síncrono |
| 2 | Aplicación web → `busqueda.router` | `GET /busqueda/documentos` · JSON/HTTPS | Síncrono |
| 3 | `busqueda.router` → `busqueda.service` | Llamada de función Python | Síncrono, in-process |
| 4 | `busqueda.service` → `documentos.service` | Llamada de función Python (interfaz de servicio, ADR 0001) | Síncrono, in-process |
| 5 | `documentos.service` → `documentos.repository` | Llamada de función Python | Síncrono, in-process |
| 6 | `documentos.repository` → SQLite | SQL | Síncrono |
| 7 | Respuesta: SQLite → ... → Aplicación web | JSON/HTTPS, cuerpo validado contra `ResultadoBusqueda` en el contrato | Síncrono |

```text
Estudiante
    |  HTTPS
    v
Aplicación web
    |  GET /busqueda/documentos  (JSON/HTTPS)
    v
busqueda.router
    |  función Python (in-process)
    v
busqueda.service
    |  función Python (in-process) — interfaz de servicio
    v
documentos.service
    |  función Python (in-process)
    v
documentos.repository
    |  SQL
    v
SQLite
```

Toda la cadena de los pasos 3 a 6 ocurre dentro del mismo proceso — no hay
llamada de red interna que decidir como síncrona o asíncrona; esa decisión
ya la fijó ADR 0001 al declarar un monolito modular. Lo que sí queda sujeto
a la decisión de esta semana es el borde del sistema (pasos 1-2 y las
integraciones de la sección 6.3).

## 6.2 Escenario: sin resultados

Si ningún documento satisface los filtros, la API devuelve HTTP 200 con
`total: 0` y una lista vacía (ver ejemplo `sinResultados` en el contrato).
Esto permite que una interfaz futura muestre un mensaje claro y sugiera
ajustar filtros. Sigue el mismo camino síncrono de la sección 6.1: no hay
una ruta de fallo especial, es una respuesta válida del mismo contrato.

## 6.3 Escenarios futuros: integraciones externas (ver ADR 0004)

Estos flujos todavía no tienen código — se documentan aquí porque la
decisión síncrono/asíncrono que los gobierna ya está tomada y debe guiar la
implementación del próximo corte.

**Publicar un documento (síncrono con almacenamiento):**

```text
Estudiante --HTTPS--> Aplicación web --JSON/HTTPS--> API backend
                                                         |
                                                REST/HTTPS (síncrono)
                                                         v
                                          Almacenamiento de archivos
```

La API espera la confirmación del almacenamiento antes de responder al
estudiante; si falla, no se crea el registro en `documentos` (sin
metadatos huérfanos).

**Notificar por correo (asíncrono, evento/outbox):**

```text
API backend --publica evento (in-process)--> Cola / outbox
                                                    |
                                     entrega asíncrona, con reintentos
                                                    v
                                          Servicio de correo (SMTP/API)
```

La API responde al estudiante sin esperar la entrega del correo. El
contrato de este evento se especificará en AsyncAPI cuando el módulo de
notificaciones entre en alcance de un corte (hoy no hay implementación que
contratar).

## Resumen de naturaleza por integración

| Integración | Naturaleza | Formato | Justificación |
|---|---|---|---|
| Aplicación web → API backend | Síncrona | JSON/HTTPS | El estudiante necesita ver el resultado en la misma interacción |
| `busqueda` → `documentos` | Síncrona, in-process | Llamada de función | Ya resuelto por ADR 0001 (monolito modular) |
| `documentos` → SQLite | Síncrona | SQL | La respuesta HTTP depende del dato leído/escrito |
| API backend → Almacenamiento | Síncrona (futura) | REST/HTTPS | Publicar sin archivo confirmado no es un resultado válido |
| API backend → Correo | Asíncrona (futura) | Evento / outbox | Efecto secundario; no debe acoplar disponibilidad del flujo crítico |

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

# 8. Conceptos transversales

El lenguaje de dominio y los contextos delimitados se documentan en docs/ddd/contextos.md, junto con la propiedad de datos por módulo (docs/ddd/propiedad-datos.md) y las violaciones detectadas con su plan de corrección (docs/ddd/auditoria-violaciones.md).


## 8.1 Separación por dominio

Cada carpeta de `app/` representa un dominio. Esto reduce cambios
transversales y facilita localizar responsabilidades.

## 8.2 Persistencia

La persistencia pertenece al módulo `documentos`. El repositorio encapsula
SQLite y expone una interfaz de servicio al resto de la aplicación.

## 8.3 Validación

Los parámetros de la API se validan con FastAPI. Por ejemplo,
`min_calificacion` acepta valores entre 0 y 5.

## 8.4 Pruebas

Las pruebas se encuentran en `tests/`. El workflow de CI ejecuta `pytest -q`
en cada `push` y `pull_request`.

## 8.5 Contrato de API

`docs/api/openapi.yaml` es la fuente única de verdad para la forma de la
API pública — se escribe antes que el código lo implemente (API-first) y
se versiona junto con él. `tests/test_contrato.py` valida en cada corrida
de `pytest` que las respuestas reales de la API cumplen ese contrato; un
cambio incompatible (campo eliminado, renombrado o de tipo distinto) hace
fallar esa prueba antes de llegar a un consumidor. La estrategia de
integración síncrona/asíncrona que acompaña al contrato está en
[`../adr/0004-integracion-sincrona-y-asincrona.md`](../adr/0004-integracion-sincrona-y-asincrona.md).

# 9. Decisiones arquitectónicas

- [ADR 0001 — Estilo arquitectónico](../adr/0001-estilo-arquitectonico.md):
  monolito modular.
- [ADR 0002 — Búsqueda combinada en una sola solicitud](../adr/0002-usabilidad-busqueda-en-una-solicitud.md).
- [ADR 0003 — Separar el contexto de Calificaciones del de Documentos](../adr/0003-separacion-contexto-calificaciones.md)
  (propuesto, pendiente de implementar).
- [ADR 0004 — Estrategia de integración síncrona y asíncrona](../adr/0004-integracion-sincrona-y-asincrona.md).
- [ADR 0008 — La métrica de búsquedas se consume por la interfaz de servicio de administración](../adr/0008-metrica-tras-interfaz-de-administracion.md).
- [ADR 0009 — No incorporar un componente generativo por ahora](../adr/0009-no-incorporar-componente-generativo.md).

# 10. Requisitos de calidad

El escenario prioritario de usabilidad exige encontrar un documento relevante
en menos de tres interacciones. La arquitectura favorece este objetivo al
mantener la búsqueda como módulo independiente y permitir filtros combinables
en una única solicitud.

La estrategia también contempla seguridad, rendimiento, disponibilidad,
mantenibilidad y escalabilidad. Las tácticas y su costo están documentados en
el ADR 0001.

# 11. Riesgos y deuda técnica

| Riesgo | Impacto | Mitigación |
|---|---|---|
| Acoplamiento entre módulos | Alto | Revisar dependencias y usar interfaces de servicio |
| SQLite no escala indefinidamente | Medio | Sustituir persistencia cuando el volumen lo justifique |
| Sin autenticación completa en este corte | Alto | Implementar control de acceso en siguientes incrementos |
| Sin almacenamiento real de archivos | Medio | Integrar servicio de archivos en un corte posterior, síncrono (ADR 0004) |
| Caché aún no implementada | Medio | Medir antes de introducirla y documentar la política de invalidación |
| Sin cola/outbox para notificaciones todavía | Medio | Implementar antes de construir el flujo de correo (ADR 0004) |
| Contrato de API sin generación automática de cliente/stub | Bajo | Evaluar generador (openapi-generator u otro) en un corte posterior |

# 12. Glosario

| Término | Definición |
|---|---|
| ShareU | Plataforma para compartir material académico |
| Monolito modular | Un único desplegable dividido en módulos de dominio |
| Módulo | Unidad de código con responsabilidad de un dominio |
| ADR | Architecture Decision Record, registro de una decisión arquitectónica |
| C4 | Modelo de documentación de arquitectura por niveles |
| Corte vertical | Funcionalidad que atraviesa varias capas hasta producir un resultado observable |
| Documento | Material académico publicado en ShareU |
| Filtro | Criterio utilizado para reducir resultados de búsqueda |
| Contrato de API | Especificación ejecutable (OpenAPI/AsyncAPI) de una interfaz, fuente única de verdad entre proveedor y consumidor |
| Prueba de contrato | Prueba automatizada que verifica que una respuesta real cumple el contrato publicado |
| Acoplamiento temporal | Grado en que el emisor de una integración debe esperar al receptor para considerar su propia operación completa |

