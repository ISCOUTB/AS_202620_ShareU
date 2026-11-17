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
