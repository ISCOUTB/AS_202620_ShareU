# 1. Introducción y objetivos

## 1.1 Descripción

ShareU es una plataforma web para estudiantes universitarios. Permite compartir y encontrar
apuntes, ejercicios, talleres, parciales y otros documentos organizados por **universidad, carrera
y materia**. El problema que ataca es concreto: el material existe, pero está disperso en grupos de
mensajería, drives personales y carpetas sin criterio común, y el estudiante pierde tiempo
buscándolo o no lo encuentra.

El sistema implementado es un **monolito modular** en Python/FastAPI con un frontend Next.js, una
base **Firestore** externa, una **caché de lectura** en proceso y un **outbox** en proceso para el
evento `documento.publicado`. La búsqueda combinada y la publicación idempotente son los dos flujos
reales; los demás módulos conservan su frontera y su endpoint de verificación.

## 1.2 Objetivos de calidad

| Objetivo | Prioridad | Indicador operacional | Evidencia |
|---|---|---|---|
| **Usabilidad** | Muy alta | Encontrar material relevante en ≤ 3 interacciones; filtros combinables en una sola solicitud | `tests/test_escenario_usabilidad.py`, `docs/evidencia/medicion-usabilidad.md` |
| **Rendimiento y costo de lectura** | Alta | p95 ≤ 500 ms, error < 1 %, ≤ 0,1 lecturas Firestore/búsqueda con caché | `docs/evidencia/mediciones/s10-*`, `s14-*` |
| **Disponibilidad controlada** | Alta | Si Firestore falla, la API responde 503 sin colgarse; publicar no depende de la bandeja | `tests/test_idempotencia.py`, `tests/test_eventos.py` |
| **Consistencia e integridad** | Alta | Publicar es idempotente; dos escritores no comparten id; un duplicado no duplica la bandeja | `tests/test_idempotencia.py`, `tests/test_eventos.py` |
| **Seguridad** | Alta | Escritura y bandeja exigen credencial; CORS y cabeceras endurecidas; sin secretos versionados | `tests/test_seguridad.py`, `docs/seguridad/amenazas.md` |
| **Mantenibilidad** | Media | Un módulo no importa archivos internos de otro; cada dato tiene un dueño | `tests/test_fronteras.py`, `docs/ddd/` |
| **Operabilidad** | Media | `/health`, logs JSON por solicitud y contadores de caché y eventos | `app/main.py`, `GET /administracion/*` |
| **Costo** | Alta (restricción) | USD 0/mes sin tarjeta, con puntos de ruptura declarados | `docs/costos/estimacion-costo.md` |

El escenario prioritario completo (fuente del estímulo, artefacto, respuesta y medida) está en
[`../aspectos.md`](../aspectos.md). La tabla de aspectos enlaza cada objetivo con su diagrama C4,
ADR, código, pruebas y evidencia.

## 1.3 Qué queda fuera

Archivos binarios y almacenamiento externo, autenticación de estudiantes, calificaciones reales,
notificaciones por correo y moderación persistente. Cada exclusión tiene su motivo y su condición
de reapertura en §11.
