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
