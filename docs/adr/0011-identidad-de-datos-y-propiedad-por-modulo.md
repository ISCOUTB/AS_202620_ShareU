# ADR 0011: Identificadores de datos y referencias entre módulos (la decisión de datos más costosa de revertir)

- **Estado:** Propuesto (pasa a Aceptado cuando el equipo lo apruebe)
- **Fecha:** octubre de 2026
- **Aspecto relacionado:** Modificabilidad
- **Origen:** Evidencia S12 — `docs/arc42/arc42.md` §8.6 a §8.8

## Contexto

Las decisiones de datos del proyecto son: el motor (SQLite, ADR 0006), la propiedad de cada dato por un solo módulo
(ADR 0001 y `docs/ddd/propiedad-datos.md`), la caché (§8.7) y el modelo de identificadores. No todas cuestan lo mismo
revertirse.

## Decisión

1. Cada entidad se identifica con un **entero autoincremental** propio de su módulo (`documentos.id`, y después
   `usuarios.id`).
2. Un módulo referencia datos de otro **solo por ese id** (`documento_id`, `usuario_id`), sin clave foránea física
   entre tablas de módulos distintos y sin copiar nombres ni textos como si fueran la fuente de verdad.
3. La ventana para cambiar el tipo de identificador sin costo **se cierra cuando existan datos reales**, es decir, al
   implementar `usuarios` o al dar persistencia real a los datos (hoy los datos son semilla y se pierden en cada
   reinicio, ADR 0006).

## Por qué es la decisión más costosa de revertir

Las otras decisiones de datos se revierten dentro de un solo lugar:

| Decisión | Costo de reversión | Dónde cambia |
|---|---|---|
| Motor SQLite → otro | Bajo | Solo `app/documentos/repository.py` (lo dice `docs/costos/estimacion-costo.md`) |
| Caché (§8.7) | Casi nulo | Son datos derivados: se borra y se reconstruye |
| Frontend (ADR 0005) | Bajo | Se comunica por HTTP/JSON |
| Propiedad por módulo | Medio | Código y ADR, sin datos de usuarios todavía |
| **Tipo e identidad de los ids** | **Alto una vez haya datos reales** | Ver abajo |

El id **sale del almacén** y se copia en todas partes. Cambiarlo después de tener datos exige:

- migrar todas las tablas que lo contienen (`documentos`, `calificaciones.documento_id`, reportes de `administracion`) con una tabla de equivalencias;
- publicar una versión mayor del contrato (`docs/api/openapi.yaml`, el campo `id` hoy es `integer`) y romper a los clientes;
- actualizar el frontend (`Documento.id: number` en `lib/api.ts`) y las pruebas;
- invalidar los enlaces y referencias que ya circulen entre estudiantes.

Hoy el costo es casi cero (5 filas de ejemplo). Crece con cada dato real. Por eso es la decisión de datos más cara
de revertir **y** la que más conviene fijar antes de que existan datos reales.

## Alternativas consideradas

### A. Entero autoincremental — elegida
- Ventaja: ya está implementado, es simple, legible en pruebas y en el contrato.
- Desventaja: revela la secuencia de creación y los ids de dos módulos no son únicos entre sí; para unir datos de dos
  bases habría que renumerar.
- Consecuencia: se acepta por simplicidad y por la regla de ids como única referencia, que mantiene posible extraer un módulo.

### B. UUID u otro identificador opaco desde ahora — descartada por ahora
- Ventaja: único globalmente, no revela secuencia, facilita unir o extraer datos.
- Desventaja: cambia el contrato, el frontend y las pruebas ahora, para un problema que aún no existe.
- **Criterio de reapertura:** antes de implementar `usuarios` o de dar persistencia real, si se prevé extraer un módulo,
  unir bases o exponer ids públicamente.

## Consecuencias

### Positivas
- Las referencias por id mantienen las fronteras del ADR 0001 y no impiden extraer un módulo (ADR 0010).
- El costo de cambio queda acotado en el tiempo y declarado.

### Negativas
- Sin claves foráneas entre módulos, la integridad referencial entre ellos la garantiza el servicio dueño, no la base de datos.
- Si se pierde la ventana, el cambio de ids es una migración con versión mayor del contrato.

## Trazabilidad

`docs/ddd/propiedad-datos.md` → este ADR → `app/documentos/repository.py`, `docs/api/openapi.yaml` →
`tests/test_fronteras.py`, `tests/test_contrato.py` → `docs/arc42/arc42.md` §8.6.
