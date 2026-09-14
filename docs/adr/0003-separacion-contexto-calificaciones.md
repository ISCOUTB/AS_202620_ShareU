# ADR 0003: Separar el contexto de Calificaciones del de Documentos

- **Estado:** Propuesto (pendiente de implementar; no se ha tocado código todavía)
- **Fecha:** septiembre de 2026
- **Origen:** auditoría de modularidad de la semana 6 —
  [`docs/ddd/auditoria-violaciones.md`](../ddd/auditoria-violaciones.md), violación V1

## Contexto

ADR 0001 define `calificaciones` como uno de los cinco módulos de dominio,
responsable de "valoración de documentos por parte de los usuarios". Sin
embargo, la implementación actual del corte vertical de búsqueda
(`app/documentos/repository.py`) guarda la calificación como una columna
fija de la tabla `documentos`, poblada una sola vez como dato semilla. El
módulo `calificaciones` no tiene tabla ni lógica; solo expone `/ping`.

Esto significa que, en el código, "calificación" hoy es un atributo
estático del documento, mientras que en el lenguaje del proyecto (y en la
intención original del ADR 0001) es el resultado de que estudiantes
valoren un documento después de usarlo. Son dos modelos distintos con el
mismo nombre — el tipo de ambigüedad que esta semana pide identificar.

## Decisión

Se separa la propiedad del dato:

- `calificaciones` pasa a tener su propia tabla
  (`documento_id`, `usuario_id`, `puntaje`, `comentario`, `fecha`) y es el
  único escritor de ese dato.
- `documentos` deja de exponer `calificacion` como parte de su interfaz
  pública (`documentos.service.obtener_documentos()`); puede conservar la
  columna en su tabla como dato heredado durante la migración, pero deja de
  tratarse como el valor oficial.
- `busqueda.service` pasa a depender de **dos** proveedores —
  `documentos.service` y `calificaciones.service` — para armar cada
  resultado (documento + promedio de calificación).

Esta es una relación **customer/supplier** en ambos casos: búsqueda no
impone su modelo a ninguno de los dos módulos, solo consume sus interfaces
públicas.

## Alternativas consideradas

### A. Dejar la calificación dentro de `documentos` — descartada

- Ventaja: no requiere cambios.
- Desventaja: perpetúa el conflicto de lenguaje; cuando se implemente
  `calificaciones` de verdad, habrá dos fuentes de verdad para el mismo
  concepto.
- Consecuencia: se descarta porque contradice directamente la
  responsabilidad que el propio ADR 0001 asignó al módulo `calificaciones`.

### B. Shared kernel entre `documentos` y `calificaciones` sobre el campo calificación — descartada

- Ventaja: evitaría una segunda consulta desde búsqueda.
- Desventaja: un shared kernel exige que ambos módulos se pongan de acuerdo
  en cada cambio de ese dato; con un equipo pequeño y calendario por corte,
  el costo de coordinación no se justifica frente a una interfaz de
  servicio simple.
- Consecuencia: se descarta a favor de la relación customer/supplier ya
  usada entre `documentos` y `busqueda`.

## Consecuencias

### Positivas

- Un solo escritor por dato: `calificaciones` escribe calificaciones,
  `documentos` escribe metadatos de documentos.
- El vocabulario del código vuelve a coincidir con el de
  `docs/aspectos/aspectos.md` y `docs/arc42/arc42.md`.
- Camino claro para implementar `calificaciones` sin retrabajo posterior.

### Negativas

- `busqueda.service` debe combinar dos fuentes en vez de una; se acepta esa
  complejidad adicional porque es la alternativa a duplicar el dato.
- Requiere migrar `tests/test_busqueda.py` y el dato semilla actual.
- Mientras no se implemente, la columna `calificacion` en `documentos`
  sigue siendo la única fuente disponible (deuda documentada, no oculta).

## Trazabilidad

- Origen del hallazgo: [`docs/ddd/auditoria-violaciones.md`](../ddd/auditoria-violaciones.md) (V1)
- Mapa de contextos: [`docs/ddd/contextos.md`](../ddd/contextos.md)
- Tabla de propiedad de datos: [`docs/ddd/propiedad-datos.md`](../ddd/propiedad-datos.md)
- ADR base: [`docs/adr/0001-estilo-arquitectonico.md`](0001-estilo-arquitectonico.md)
