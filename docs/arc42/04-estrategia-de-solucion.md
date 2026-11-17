# 4. Estrategia de solución

La estrategia es un **monolito modular**. El sistema tiene un único
desplegable, pero cada dominio mantiene una responsabilidad y una frontera
explícita.

La comparación de alternativas está en
[`../aspectos/aspectos.md`](../aspectos/aspectos.md). La decisión arquitectónica
base está en [`../adr/0001-estilo-arquitectonico.md`](../adr/0001-estilo-arquitectonico.md)
y la decisión específica del flujo de búsqueda en
[`../adr/0002-usabilidad-busqueda-en-una-solicitud.md`](../adr/0002-usabilidad-busqueda-en-una-solicitud.md).

## Módulos

- **usuarios:** registro, autenticación y perfiles.
- **documentos:** clasificación y persistencia de documentos.
- **busqueda:** filtros y ordenamiento de resultados.
- **calificaciones:** valoración de documentos.
- **administracion:** reportes y moderación.

La regla principal es que un módulo no accede directamente a la persistencia
interna de otro. Cuando necesita información, utiliza la interfaz de servicio
pública del módulo correspondiente.
