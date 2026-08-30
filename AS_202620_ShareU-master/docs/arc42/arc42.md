---
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
- El proyecto se entrega incrementalmente.
- El despliegue inicial es un único servicio.
- Los cinco dominios deben conservar fronteras explícitas.
- La persistencia del corte vertical utiliza SQLite y la biblioteca estándar
  de Python para mantener el alcance pequeño.
- Las pruebas se ejecutan con `pytest`.
- La integración continua se realiza con GitHub Actions.
- Las decisiones arquitectónicas se registran mediante ADR.

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
[`../aspectos/aspectos.md`](../aspectos/aspectos.md), y la decisión formal en
[`../adr/0001-estilo-arquitectonico.md`](../adr/0001-estilo-arquitectonico.md).

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

## Escenario: buscar material

1. El estudiante solicita `/busqueda/documentos`.
2. El router recibe los filtros opcionales.
3. `busqueda.service` obtiene documentos mediante la interfaz pública de
   `documentos.service`.
4. El repositorio consulta SQLite.
5. El servicio de búsqueda aplica filtros y ordena resultados.
6. FastAPI devuelve el total y los documentos relevantes.

## Escenario: sin resultados

Si ningún documento satisface los filtros, la API devuelve HTTP 200 con
`total: 0` y una lista vacía. Esto permite que una interfaz futura muestre un
mensaje claro y sugiera ajustar filtros.

# 7. Vista de despliegue

La primera versión se ejecuta como un único servicio:

```text
+-----------------------------+
| Entorno de ejecución        |
|                             |
|  Uvicorn                    |
|    |                        |
|    +-- FastAPI / ShareU     |
|           |                 |
|           +-- SQLite        |
+-----------------------------+
```

En una evolución posterior, el almacenamiento de archivos y el correo podrán
ser servicios externos. Si el rendimiento de un dominio lo exige, el ADR 0001
permite evaluar la extracción del módulo correspondiente.

# 8. Conceptos transversales

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

# 9. Decisiones arquitectónicas

- [ADR 0001 — Estilo arquitectónico](../adr/0001-estilo-arquitectonico.md):
  monolito modular.

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
| Sin almacenamiento real de archivos | Medio | Integrar servicio de archivos en un corte posterior |
| Caché aún no implementada | Medio | Medir antes de introducirla y documentar la política de invalidación |

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
