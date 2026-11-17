# C4 — Nivel 2: contenedores

Diagrama editable: [`nivel2.mmd`](nivel2.mmd). Nivel 1: [`nivel1.mmd`](nivel1.mmd). El diagrama
refleja el sistema **implementado**, no el objetivo: si algo no existe (broker, almacenamiento de
archivos, correo), no aparece como contenedor activo.

## Contenedores y componentes desplegables

| Elemento | Tecnología | Responsabilidad | Dónde |
|---|---|---|---|
| **Aplicación web** | Next.js 14 (React), contenedor `web` | Interfaz de búsqueda y publicación; timeout y reintento del cliente | `app/frontend/` |
| **API backend** | Python 3.11 + FastAPI, contenedor `api` | API HTTP, validación, seguridad, composición y logging | `app/` |
| **Firestore** | Firebase, plan Spark; contenedor de datos **externo** (`ContainerDb_Ext`) | Persistencia de metadatos | Google Cloud |
| **Caché de lectura** | Memoria del proceso, TTL 60 s | Lista pública de documentos e invalidación tras escritura | `app/documentos/repository.py` |
| **Outbox** | Memoria del proceso | Publicación, reintentos, deduplicación, DLQ | `app/eventos/outbox.py` |
| **Módulos** | Funciones Python | `usuarios`, `documentos`, `busqueda`, `calificaciones`, `administracion` | `app/<modulo>/` |

Firestore se dibuja como **contenedor de datos externo** (`ContainerDb_Ext`) porque es un almacén
con esquema, credenciales y límites propios, no una caja negra genérica. No se dibuja ningún broker:
el outbox es una lista en memoria dentro del proceso de la API y no sobrevive a un reinicio, por lo
que presentarlo como contenedor independiente sería falso.

## Módulos internos del backend

```text
app.main (composición)
  |
  +--> usuarios.router
  +--> documentos.router ----> documentos.service ----> documentos.repository ----> Firestore
  |                                   |                         |
  |                                   |                         +--> caché
  |                                   +--> eventos.publicar --> outbox --> administracion.revision
  +--> busqueda.router ------> busqueda.service ----> documentos.service
  |                                          +-----> administracion.service
  +--> calificaciones.router
  +--> administracion.router -> administracion.service (métricas, revisión, eventos, caché)
```

Cada módulo expone `router → service → repository`; los cruces permitidos son los que pasan por
`service.py` y los verifica `tests/test_fronteras.py`.

## Protocolos y formatos en cada relación

| Origen → destino | Protocolo / formato | Naturaleza |
|---|---|---|
| Estudiante / administrador → web | HTTPS | Síncrona |
| web → API | JSON/HTTPS; timeout 15 s, 1 reintento; `X-Request-ID`, `X-Admin-Token` en escritura | Síncrona |
| API → módulos | Llamada de función Python | In-process |
| busqueda → documentos | Función Python (interfaz de servicio) | In-process |
| busqueda → administración | Función Python (métrica, ADR 0008) | In-process |
| documentos → caché | Memoria compartida del proceso | In-process |
| documentos → Firestore | gRPC/HTTPS vía `firebase-admin`; timeout 2 s, 3 intentos | Síncrona |
| documentos → outbox | Función Python; JSON del contrato v1 | In-process |
| outbox → administración | Función Python; asíncrona después de la respuesta HTTP | In-process, al menos una vez |

## Corte vertical implementado

```text
Estudiante
    |  HTTPS
    v
Web (Next.js)
    |  GET /busqueda/documentos?materia=Programación  (JSON/HTTPS)
    v
API FastAPI
    |
    v
busqueda.router -> busqueda.service -> documentos.service -> documentos.repository
                                                              |          |
                                                        caché (hit)   Firestore (miss)
                                                              |
                                                              v
                                                    JSON con total y resultados
```

La búsqueda combina universidad, carrera, materia, tipo, palabra clave y calificación mínima en una
sola solicitud, y ordena por calificación descendente. Los resultados incluyen título, universidad,
carrera, materia, tipo, autor y calificación.

## Flujo de publicación y evento

```text
Administrador
    |  POST /documentos  (JSON/HTTPS, X-Admin-Token, Idempotency-Key)
    v
documentos.router -> documentos.service -> documentos.repository -> Firestore
       |                                        |
       |                                        +--> invalida caché
       +--> publica documento.publicado --> outbox (memoria)
       |
       +--> 201/200/409/503
                              (después de responder)
                              outbox --> administracion.revision
```

## Trazabilidad

- Estilo y fronteras: [`../adr/0001-estilo-arquitectonico.md`](../adr/0001-estilo-arquitectonico.md)
- Usabilidad: [`../adr/0002-usabilidad-busqueda-en-una-solicitud.md`](../adr/0002-usabilidad-busqueda-en-una-solicitud.md)
- Persistencia: [`../adr/0012-persistencia-en-firestore.md`](../adr/0012-persistencia-en-firestore.md)
- Caché: [`../adr/0013-cache-de-lectura-con-invalidacion.md`](../adr/0013-cache-de-lectura-con-invalidacion.md)
- Eventos: [`../adr/0015-mensajeria-asincrona-con-outbox.md`](../adr/0015-mensajeria-asincrona-con-outbox.md)
- Aspectos y códigos: [`../aspectos.md`](../aspectos.md)
- Implementación: `app/busqueda/`, `app/documentos/`, `app/eventos/`, `app/administracion/`
- Pruebas: `tests/test_busqueda.py`, `tests/test_cache.py`, `tests/test_eventos.py`
