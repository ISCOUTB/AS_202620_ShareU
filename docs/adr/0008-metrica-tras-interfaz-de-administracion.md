# ADR 0008: La métrica de búsquedas se consume por la interfaz de servicio de administración

- **Estado:** Propuesto (pasa a Aceptado cuando el equipo lo apruebe)
- **Fecha:** septiembre de 2026
- **Aspecto relacionado:** Usabilidad
- **Origen:** auditoría de erosión de la semana 9 (hallazgo E1 en
  [`docs/evidencia/evidencia-s9.md`](../evidencia/evidencia-s9.md))

## Contexto

En la semana 8 se agregó, con apoyo de IA, la métrica `tasa_busquedas_sin_resultados`
para vigilar el escenario de usabilidad (`docs/aspectos/aspectos.md`): una búsqueda
sin resultados obliga a una interacción extra y erosiona el presupuesto de 3.

La generación resolvió el registro de la métrica con un atajo:
`app/busqueda/service.py` importaba `app.administracion.metricas` (un archivo
interno de otro módulo). Eso contradice la regla 3 del ADR 0001 («otro módulo
consume servicios públicos») y deja desactualizada la afirmación de
`docs/ddd/propiedad-datos.md` de que el único cruce entre módulos era
`busqueda -> documentos.service`. Nadie lo notó en revisión porque las pruebas
pasaban.

## Restricciones del proyecto que pesan en la decisión

- Monolito modular con un solo escritor por dato (ADR 0001, `propiedad-datos.md`).
- Costo USD 0 y sin tarjeta; el backend gratuito no tiene disco persistente
  (`docs/arc42/arc42.md` §2 y §7.1).
- Equipo pequeño: la solución debe ser la más simple que mantenga la frontera.

## Decisión

1. `administracion` publica `app/administracion/service.py` como su interfaz
   pública; `busqueda` solo importa desde ahí.
2. Los contadores siguen en memoria dentro de `administracion` (único dueño y
   único escritor de ese dato).
3. Se agrega `tests/test_fronteras.py`: falla si un módulo importa algo distinto
   de `service` de otro módulo. La regla deja de depender de que un revisor la vea.

## Alternativas consideradas

### A. Dejar el import y actualizar `propiedad-datos.md` — descartada
- Ventaja: cero cambios de código.
- Desventaja: normaliza saltarse la interfaz; el siguiente atajo generado
  (`.repository`, `.metricas`) pasaría igual.

### B. Registrar la métrica en el middleware de `app/main.py` — descartada
- Ventaja: `busqueda` no depende de `administracion`.
- Desventaja: `main.py` es punto de composición sin lógica de dominio
  (arc42 §5.1) y el middleware no conoce el total de resultados sin leer la respuesta.

### C. Persistir la métrica en SQLite con tabla propia — descartada por ahora
- Ventaja: sobrevive a reinicios y a varias réplicas.
- Desventaja: sin disco persistente en el plan gratuito no aporta valor hoy, y
  agrega una tabla y un repositorio más.
- **Criterio de reapertura:** si el despliegue pasa a más de una réplica o a un
  plan con disco persistente.

### D. Fachada `administracion/service.py` — elegida
- Ventaja: cinco líneas, misma frontera que ya usan `busqueda -> documentos`.
- Consecuencia: `busqueda` sigue dependiendo de `administracion`; la dependencia
  queda declarada aquí y en el C4 nivel 2.

## Medición

- **Frontera:** `tests/test_fronteras.py` (0 cruces prohibidos).
- **Escenario:** `tests/test_escenario_usabilidad.py` mide las interacciones
  mínimas (campos llenados + clic en Buscar) para encontrar cada documento del
  catálogo; umbral <= 3; resultado actual: 2 para los 5 documentos.
- **Métrica en ejecución:** `GET /administracion/metricas`.

## Consecuencias

### Positivas
- La regla de ADR 0001 queda ejecutable y no solo escrita.
- Otro módulo puede leer la métrica sin conocer su almacenamiento.

### Negativas
- Un archivo más por módulo que exponga interfaz.
- El contador en memoria sigue siendo impreciso con varias réplicas.

## Trazabilidad

`docs/aspectos/aspectos.md` -> este ADR -> `app/administracion/service.py`,
`app/busqueda/service.py` -> `tests/test_fronteras.py`,
`tests/test_escenario_usabilidad.py`, `tests/test_metricas.py` ->
`docs/evidencia/evidencia-s9.md`.
