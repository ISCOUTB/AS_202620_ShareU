# ADR 0001: Estilo arquitectónico

## Estado
Aceptado

## Contexto
El equipo necesita un punto de partida simple que permita crecer por
dominios sin acoplar módulos entre sí desde el inicio.

## Decisión
Se adopta un **monolito modular**: cada dominio vive en `app/<modulo>/`
con su propio router (y, cuando aplica, `service.py` y `repository.py`).
Ningún módulo importa el modelo interno de otro; la comunicación entre
módulos pasa por la interfaz pública (`service.py`) del módulo dueño de
los datos.

## Consecuencias
- Fácil de ejecutar y probar como una sola aplicación.
- Los límites de módulo quedan explícitos desde el primer commit.
- Si un dominio crece demasiado, puede extraerse a un servicio propio
  sin rediseñar el resto.
