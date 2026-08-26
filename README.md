# AS_202620_ShareU
Problema: 
Los estudiantes suelen perder tiempo buscando apuntes, ejercicios o material de determinadas materias.

Propósito: 
Crear una plataforma para compartir material académico organizado por universidad, carrera y materia.

## Arquitectura

Estilo: monolito modular (ver [`docs/adr/0001-estilo-arquitectonico.md`](docs/adr/0001-estilo-arquitectonico.md)
y la sección "Solution Strategy" de [`docs/arc42-template-EN.md`](docs/arc42-template-EN.md)).
Módulos: `usuarios`, `documentos`, `busqueda`, `calificaciones`, `administracion`.
Cada uno vive en `app/<modulo>/` con su propio router; todavía sin lógica de
negocio (fontanería para el corte vertical de la semana 4).
