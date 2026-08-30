# C4 — Nivel 2: Contenedores

## Alcance

Este nivel describe los contenedores principales de ShareU y sus
responsabilidades. El diagrama editable de nivel 1 se encuentra en
[`nivel1.mmd`](nivel1.mmd).

## Contenedores

| Contenedor | Tecnología | Responsabilidad |
|---|---|---|
| Aplicación web | HTML, CSS, JavaScript | Interfaz utilizada por estudiantes y administradores |
| API backend | Python + FastAPI | Expone la API HTTP y coordina los módulos del monolito |
| Base de datos | SQLite en el corte vertical; SQL relacional como objetivo | Persistencia de usuarios, documentos, calificaciones y reportes |
| Almacenamiento de archivos | Servicio externo | Guarda y recupera los archivos académicos |
| Servicio de correo | SMTP/API | Envía notificaciones transaccionales |

## Organización interna del backend

La API backend contiene cinco módulos de dominio:

- **usuarios:** registro, autenticación y perfil.
- **documentos:** clasificación y persistencia de los metadatos de documentos.
- **busqueda:** filtros y ordenamiento de resultados.
- **calificaciones:** valoración de documentos.
- **administracion:** reportes, moderación y gestión administrativa.

Los módulos se mantienen dentro de un único desplegable, de acuerdo con el
ADR 0001. Cada módulo tiene una responsabilidad de dominio clara y los
accesos entre módulos se realizan mediante interfaces de servicio, evitando
que un módulo acceda directamente a las tablas internas de otro.

## Corte vertical implementado

El recorrido funcional de la semana 4 es:

```text
Estudiante
    |
    | GET /busqueda/documentos
    | filtros opcionales
    v
API FastAPI
    |
    v
busqueda.router
    |
    v
busqueda.service
    |
    | interfaz pública
    v
documentos.service
    |
    v
documentos.repository
    |
    v
SQLite
```

La búsqueda permite combinar en una sola solicitud:

- universidad;
- carrera;
- materia;
- tipo de documento;
- palabra clave;
- calificación mínima.

Los resultados incluyen la información necesaria para que el estudiante
pueda reconocer el material sin abrir cada publicación: título, materia,
tipo, autor y calificación.

## Trazabilidad

- Decisión arquitectónica: [`../adr/0001-estilo-arquitectonico.md`](../adr/0001-estilo-arquitectonico.md)
- Escenario de usabilidad: [`../aspectos/aspectos.md`](../aspectos/aspectos.md)
- Implementación: `app/busqueda/` y `app/documentos/`
- Pruebas: `tests/test_busqueda.py`
