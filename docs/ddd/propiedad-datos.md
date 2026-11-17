# Propiedad de datos: quién escribe qué

Regla aplicada: **cada dato tiene exactamente un módulo que escribe**; los demás solo leen o piden, y
siempre a través de la interfaz de servicio pública del módulo dueño (nunca del repositorio interno).

## Estado actual del código

| Dato / colección | Dueño (único escritor) | Cómo escribe | Quién lee | Cómo lee | Estado |
|---|---|---|---|---|---|
| Colección `documentos` (id, titulo, universidad, carrera, materia, tipo, autor, calificacion, palabras_clave, idempotency_*, creado_en) | `documentos` | `documentos/repository.py` sobre Firestore | `busqueda` | `documentos.service.obtener_documentos()` | Dueño único y acceso por interfaz |
| Caché de lectura de documentos | `documentos` | `_CacheDocumentos.guardar` e `invalidar` | `busqueda` (indirectamente) | `documentos.service` | Derivada; se reconstruye y no es fuente de verdad |
| Columna lógica `calificacion` | `documentos` (dato semilla) | `repository.py` | `busqueda` | `documentos.service` | Dueño técnico correcto, dueño **conceptual** equivocado (V1) |
| Bandeja de revisión (`id_documento`, `titulo`, `materia`, `autor`, `event_id`, `correlation_id`) | `administracion` | `revision.registrar_para_revision` (consumidor) y `resolver_revision` | `GET /administracion/revision` | `administracion.service` | Dueño único; en memoria |
| Outbox (`Evento`: `event_id`, `tipo`, `version`, `payload`, estado) | `eventos` | `eventos.publicar`, `despachar`, `reenviar` | `documentos.router` (publica), `administracion.revision` (consume), `GET /administracion/eventos` | `eventos` | Mecanismo, no dato de negocio; en memoria |
| Contadores de métricas de búsqueda | `administracion` | `administracion/metricas.py` (memoria) | `busqueda` (registra), `GET /administracion/metricas` | `administracion.service` (ADR 0008) | Dueño único; efímero |
| Resultados de búsqueda | Ninguno (no persiste) | n/a | Frontend (`app/frontend/lib/api.ts`) | `GET /busqueda/documentos` | Correcto: proyección de solo lectura |
| Calificaciones de estudiantes (puntaje, autor, fecha) | *No existe* | — | — | — | El módulo solo expone `/ping` (V1) |
| Cuentas de usuario (credenciales, perfil, rol) | *No existe* | — | — | — | El módulo solo expone `/ping` (V2) |
| Reportes / acciones de moderación persistentes | *No existe* | — | — | — | La bandeja es efímera; no hay historial |

## Regla de escritura para lo que falta

| Dato futuro | Dueño esperado | Quién NO debe escribirlo directamente |
|---|---|---|
| Cuenta / perfil de usuario | `usuarios` | `documentos` (autor), `administracion` (moderación), `calificaciones` (autor) |
| Calificación de un documento | `calificaciones` | `documentos`; debe dejar de exponer `calificacion` como valor oficial (ADR 0003) |
| Reporte / sanción / retiro | `administracion` | `documentos` y `usuarios` no marcan sus propios registros; exponen una operación que administración invoca |
| Historial de moderación | `administracion` | Nadie más; hoy la bandeja no se persiste |

## Cómo se verificó

1. Imports que crucen de un módulo al `repository.py` de otro: las únicas dependencias entre módulos
   son `busqueda.service` → `documentos.service`, `busqueda.service` → `administracion.service`,
   `documentos.router` → `eventos`/`seguridad` y `administracion.revision` → `eventos`. Las verifica
   `tests/test_fronteras.py`.
2. Columnas de una colección que representen conceptos de otro dominio: se mantiene
   `calificacion` dentro de `documentos`, registrado como V1 con su plan.

```bash
grep -rn "^from app\." app --include="*.py" | grep -v "app.main"
```

El resultado confirma que ningún módulo importa el repositorio de otro.
