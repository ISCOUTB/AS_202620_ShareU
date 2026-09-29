# ADR 0009: No incorporar un componente generativo en ShareU por ahora

- **Estado:** Propuesto (pasa a Aceptado cuando el equipo lo apruebe)
- **Fecha:** septiembre de 2026
- **Aspecto relacionado:** Usabilidad

## Contexto

Se evaluó si un modelo generativo dentro del sistema (por ejemplo, búsqueda en
lenguaje natural o resúmenes de documentos) ayudaría al escenario prioritario:
encontrar material relevante en 3 interacciones o menos.

## Decisión

**No se incorpora** un componente generativo en este semestre. La búsqueda
seguirá siendo filtrado determinista sobre el módulo `busqueda`.

## Razones (con las restricciones del proyecto)

- **El escenario ya se cumple sin él:** con los datos de ejemplo, cada documento
  se encuentra en 2 interacciones (`tests/test_escenario_usabilidad.py`, umbral 3).
- **Costo:** la restricción es USD 0/mes y sin tarjeta en ningún proveedor
  (`docs/arc42/arc42.md` §2). Un modelo por API se cobra por llamada y suele
  exigir tarjeta; una cuota gratuita puede cambiar sin aviso.
- **Disponibilidad y latencia:** agregaría un proveedor externo en el camino de
  la búsqueda, el flujo más importante. Hoy la búsqueda es una llamada
  in-process que responde en un par de milisegundos (`duration_ms` en los logs
  locales); una llamada a un modelo añade red y tiempo variable, y habría que
  definir qué se muestra cuando el proveedor falla.
- **Simplicidad y alcance:** exige conjunto de evaluación, control de costo y
  modelado de amenazas (semana 13) que el equipo no puede sostener junto con
  usuarios, calificaciones y administración.

## Alternativa considerada

### Incorporarlo como asistente de búsqueda opcional — descartada por ahora
- Ventaja: consultas en lenguaje natural.
- Desventaja: costo, dependencia externa y superficie de ataque por la entrada
  del usuario, sin un problema medido que lo justifique.

## Criterio de reapertura

Reabrir este ADR si se cumple alguno:
- `tasa_busquedas_sin_resultados` (`GET /administracion/metricas`) se mantiene
  por encima del umbral que fije el equipo (propuesta: 30 %) y los filtros no
  lo corrigen.
- Aparece un proveedor con cuota gratuita estable y sin tarjeta.
- El curso pide el componente generativo como requisito.

Si se reabre, el nuevo ADR debe declarar el comportamiento ante fallo o
degradación del proveedor, y el componente aparecerá en el C4 nivel 2 como
contenedor externo con su protocolo y costo.

## Consecuencias

- Positivas: sin costo, sin dependencia nueva, sin riesgo de entrada hostil.
- Negativas: sin búsqueda en lenguaje natural; el estudiante depende de filtros
  y palabras clave.
