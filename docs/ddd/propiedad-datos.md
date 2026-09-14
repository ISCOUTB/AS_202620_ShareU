# Propiedad de datos: quién escribe qué — Semana 6

Regla aplicada: **cada dato tiene exactamente un módulo que escribe**; los
demás solo leen o piden, y siempre a través de la interfaz de servicio
pública del módulo dueño (nunca del repositorio interno).

## Estado actual del código

| Dato / tabla | Dueño (único escritor) | Cómo escribe | Quién lee | Cómo lee | Estado |
|---|---|---|---|---|---|
| Tabla `documentos` (id, titulo, universidad, carrera, materia, tipo, autor, palabras_clave) | `documentos` | `documentos/repository.py` (SQLite) | `busqueda` | `documentos.service.obtener_documentos()` (interfaz pública) | ✅ Dueño único, acceso correcto por interfaz |
| Columna `calificacion` (dentro de la tabla `documentos`) | `documentos` (por defecto, como dato semilla) | `documentos/repository.py` | `busqueda` | vía `documentos.service` | ⚠️ Dueño técnico correcto (un solo escritor), pero dueño **conceptual** equivocado: el dato pertenece al lenguaje de `calificaciones`, que no lo escribe ni lo conoce. Ver violación V1. |
| Calificaciones de estudiantes (puntaje, autor, fecha) | *No existe tabla todavía* | — | — | — | ⚠️ El módulo `calificaciones` no tiene persistencia; solo expone `/ping` |
| Cuentas de usuario (credenciales, perfil, rol) | *No existe tabla todavía* | — | — | — | Pendiente — módulo `usuarios` solo expone `/ping` |
| Reportes / acciones de moderación | *No existe tabla todavía* | — | — | — | Pendiente — módulo `administracion` solo expone `/ping` |
| Resultados de búsqueda | Ninguno (no persiste) | n/a | Frontend (`app/frontend/script.js`) | `GET /busqueda/documentos` | ✅ Correcto: búsqueda es una proyección de solo lectura, no debe tener tabla propia |

## Regla de escritura para lo que falta por implementar

Para que cuando se implementen `usuarios`, `calificaciones` y
`administracion` no se repita la mezcla ya detectada en `documentos`, se
fija de una vez la propiedad esperada:

| Dato futuro | Dueño esperado | Quién NO debe escribirlo directamente |
|---|---|---|
| Cuenta / perfil de usuario | `usuarios` | `documentos` (autor), `administracion` (moderación), `calificaciones` (autor de la valoración) — todos deben pedirlo por interfaz |
| Calificación de un documento | `calificaciones` | `documentos` — debe dejar de tener la columna `calificacion` propia (ver ADR 0003) |
| Reporte / sanción / retiro de contenido | `administracion` | `documentos` y `usuarios` no deben marcar sus propios registros como "reportados" o "suspendidos"; exponen una operación que `administracion` invoca, y el estado resultante lo guarda quien lo pidió, no quien lo ejecuta |

## Cómo se verificó

Se revisó cada `router.py`/`service.py`/`repository.py` del repositorio
buscando:

1. Imports que crucen de un módulo al `repository.py` de otro (ninguno
   encontrado — la única dependencia entre módulos es
   `busqueda.service` → `documentos.service`, que es la interfaz pública).
2. Columnas de una tabla que representen conceptos de otro dominio
   (encontrado: `calificacion` dentro de `documentos`).

```bash
grep -rn "^from app\." app --include="*.py" | grep -v "app.main"
```

Este comando confirma que el único cruce entre módulos hoy es
`app/busqueda/service.py: from app.documentos.service import obtener_documentos`,
que es exactamente la relación permitida por ADR 0001.
