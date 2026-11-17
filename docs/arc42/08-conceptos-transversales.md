# 8. Conceptos transversales

El lenguaje de dominio y los contextos delimitados se documentan en docs/ddd/contextos.md, junto con la propiedad de datos por módulo (docs/ddd/propiedad-datos.md) y las violaciones detectadas con su plan de corrección (docs/ddd/auditoria-violaciones.md).


## 8.1 Separación por dominio

Cada carpeta de `app/` representa un dominio. Esto reduce cambios
transversales y facilita localizar responsabilidades.

## 8.2 Persistencia

La persistencia pertenece al módulo `documentos`. El repositorio encapsula
SQLite y expone una interfaz de servicio al resto de la aplicación.

## 8.3 Validación

Los parámetros de la API se validan con FastAPI. Por ejemplo,
`min_calificacion` acepta valores entre 0 y 5.

## 8.4 Pruebas

Las pruebas se encuentran en `tests/`. El workflow de CI ejecuta `pytest -q`
en cada `push` y `pull_request`.

## 8.5 Contrato de API

`docs/api/openapi.yaml` es la fuente única de verdad para la forma de la
API pública — se escribe antes que el código lo implemente (API-first) y
se versiona junto con él. `tests/test_contrato.py` valida en cada corrida
de `pytest` que las respuestas reales de la API cumplen ese contrato; un
cambio incompatible (campo eliminado, renombrado o de tipo distinto) hace
fallar esa prueba antes de llegar a un consumidor. La estrategia de
integración síncrona/asíncrona que acompaña al contrato está en
[`../adr/0004-integracion-sincrona-y-asincrona.md`](../adr/0004-integracion-sincrona-y-asincrona.md).
