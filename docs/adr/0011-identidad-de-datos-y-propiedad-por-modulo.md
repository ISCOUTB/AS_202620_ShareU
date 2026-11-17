# ADR 0011: Identificadores de datos y referencias entre módulos (la decisión de datos más costosa de revertir)

- **Estado:** Aceptado
- **Fecha:** octubre de 2026, revisado en noviembre de 2026
- **Aspecto relacionado:** Modificabilidad / Integridad
- **Origen:** Evidencia S12; `docs/datos/consistencia.md`

## Contexto

Las decisiones de datos del proyecto son: el motor (Firestore, ADR 0012), la propiedad de cada
dato por un solo módulo (ADR 0001 y `docs/ddd/propiedad-datos.md`), la caché (ADR 0013) y el
modelo de identificadores. No todas cuestan lo mismo revertirse. Firestore **no tiene
autoincremento**, así que el id entero hay que reservarlo explícitamente.

## Decisión

1. Cada documento se identifica con un **entero** (`documentos.id`). El id del documento en
   Firestore es ese mismo número como texto (`collection.document("7")`).
2. La reserva del id es **fuerte y atómica**: `_reservar_id_y_crear` calcula el primer candidato
   (`máximo + 1`) y usa `DocumentReference.create()`, que falla con `AlreadyExists` si otro
   escritor tomó ese id; entonces prueba el siguiente. No se usa `set()` porque sobrescribiría.
3. Un módulo referencia datos de otro **solo por ese id** (`documento_id`, `usuario_id`), sin
   copiar nombres ni textos como fuente de verdad y sin claves foráneas físicas entre colecciones
   de módulos distintos.
4. El tipo de id es parte del contrato público (`docs/api/openapi.yaml`, `id: integer`) y del
   frontend (`Documento.id: number`). Cambiarlo es un cambio incompatible.

## Por qué es la decisión de datos más costosa de revertir

Las otras decisiones de datos se revierten dentro de un solo lugar:

| Decisión | Costo de reversión | Dónde cambia |
|---|---|---|
| Motor Firestore → otro | Bajo/medio | Solo `app/documentos/repository.py` (ADR 0012) |
| Caché (ADR 0013) | Casi nulo | Datos derivados: se borra y se reconstruye |
| Frontend (ADR 0005) | Bajo | Se comunica por HTTP/JSON |
| Propiedad por módulo | Medio | Código y ADR, sin datos de usuarios todavía |
| **Tipo e identidad de los ids** | **Alto en cuanto haya datos reales** | Ver abajo |

El id **sale del almacén** y se copia en todas partes. Cambiarlo después de tener datos exige:

- migrar todos los documentos y las referencias (`calificaciones.documento_id`, reportes de
  `administracion`) con una tabla de equivalencias;
- publicar una **versión mayor** del contrato y romper a los clientes;
- actualizar el frontend (`Documento.id: number`) y las pruebas;
- invalidar enlaces y referencias que ya circulen entre estudiantes.

Hoy el costo es bajo (5 documentos de ejemplo). Crece con cada dato real. Por eso es la decisión
de datos más cara de revertir **y** la que conviene fijar antes de que existan datos reales.

## Alternativas consideradas

### A. Entero reservado con `create()` — elegida
- Ventaja: legible en pruebas y en el contrato; la unicidad la garantiza Firestore, no una
  convención del código; no hay que cambiar frontend ni contrato.
- Desventaja: revela la secuencia de creación; ante muchos escritores concurrentes puede haber
  colisiones y reintentos (se prueban 5 candidatos).

### B. UUID o id automático de Firestore desde ahora — descartada por ahora
- Ventaja: único globalmente, no revela secuencia, facilita unir o extraer datos.
- Desventaja: rompe el contrato y el frontend ahora, para un problema que aún no existe; además
  encarece las pruebas legibles.
- **Criterio de reapertura:** antes de implementar `usuarios`, de unir dos bases o de exponer ids
  como enlaces públicos permanentes.

## Consecuencias

### Positivas
- Las referencias por id mantienen las fronteras del ADR 0001 y no impiden extraer un módulo
  (ADR 0010).
- La publicación concurrente no duplica ids: `test_dos_publicaciones_no_repiten_id` y
  `test_reservar_id_salta_un_id_que_otro_escritor_tomo`.

### Negativas
- Sin claves foráneas entre módulos, la integridad referencial la garantiza el servicio dueño.
- Si se pierde la ventana, el cambio de ids es una migración con versión mayor del contrato.
- La reserva por «máximo + 1» hace una lectura extra antes de escribir; es aceptable con el
  volumen actual y está cubierta por la caché solo en lectura, no en la reserva.

## Trazabilidad

`docs/datos/consistencia.md` → este ADR → `app/documentos/repository.py`
(`_reservar_id_y_crear`) → `tests/test_idempotencia.py` → `docs/api/openapi.yaml` (campo `id`) →
arc42 §8.6.
