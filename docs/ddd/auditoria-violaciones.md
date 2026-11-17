# Auditoría de modularidad — violaciones y plan de corrección

Método: revisión de imports entre módulos (`app/*/service.py`, `repository.py`, `router.py`), de las
colecciones de Firestore y de los datos que la API expone, contrastados con el lenguaje de
[`../aspectos.md`](../aspectos.md) y el arc42.

## V1 — "Calificación" mezclada dentro del contexto Documentos

**Dónde:** `app/documentos/repository.py`, campo `calificacion` del documento; `busqueda.service`
ordena por él.

**Qué pasa:** el valor es un dato semilla estático. No existe módulo `calificaciones` con
persistencia propia; `app/calificaciones/router.py` solo responde `/ping`. El sistema trata la
calificación como atributo fijo del documento, no como el resultado de valoraciones de estudiantes.

**Por qué es una violación de límites:** el nombre ya significa "valoración por usuarios" en
[`../aspectos.md`](../aspectos.md) y en el arc42. Si mañana se implementa `calificaciones` con su
propia colección sin corregir esto, habría dos fuentes de verdad para "la calificación de un
documento".

**Severidad:** alta. **Estado:** abierta, con ADR 0003 redactado.

**Plan de corrección:**

1. Crear `app/calificaciones/repository.py` con colección `calificaciones(id, documento_id,
   usuario_id, puntaje, comentario, fecha)`.
2. Exponer `registrar_calificacion(...)` y `obtener_promedio(documento_id)` en su `service.py`.
3. Dejar de exponer `calificacion` como valor oficial en `documentos.service`.
4. Combinar en `busqueda.service` documentos + promedio y ordenar por el promedio.
5. Actualizar pruebas y el contrato.
6. Registrar el cambio en ADR 0003 y actualizar C4 y arc42 §8.

## V2 — "Autor" como texto libre en vez de referencia a Usuarios

**Dónde:** `documentos.autor` es una cadena; el evento copia `autor` como texto.

**Qué pasa:** no hay referencia a `usuarios` (que aún no existe). Cuando exista, "quién publicó"
tendrá dos representaciones que pueden divergir: el nombre guardado y el perfil real.

**Severidad:** media. **Estado:** abierta, preventiva.

**Plan:** al implementar `usuarios`, agregar `autor_id` como referencia y tratar el nombre
desnormalizado como caché de lectura, nunca como fuente de verdad.

## V3 — Usuarios y Administración sin implementación completa

**Dónde:** `app/usuarios/router.py` (solo `/ping`); `administracion` tiene métricas, bandeja y
resolución, pero **no** persiste historial ni identifica al administrador.

**Qué pasa:** no hay doble escritor hoy, pero `administracion` actúa sobre documentos y la bandeja es
efímera. Si se implementa moderación escribiendo directamente en `documentos` "porque es más
rápido", se reproduce el antipatrón.

**Severidad:** baja hoy, alta si no se deja la regla escrita. **Estado:** regla documentada y
prueba de fronteras en verde.

**Plan preventivo:** `administracion` debe invocar operaciones de `documentos.service` (por ejemplo
`retirar_documento(id)`) en vez de tocar su repositorio. Persistir la bandeja y el historial es
trabajo futuro declarado.

## V4 — Sin capa anticorrupción para servicios externos futuros

**Dónde:** almacenamiento de archivos y correo no existen; Firestore sí está integrado, pero
encapsulado en `repository.py`.

**Qué pasa:** la integración con Firestore ya respeta la frontera (solo `repository.py` conoce el SDK).
Las integraciones futuras podrían no hacerlo.

**Severidad:** baja. **Estado:** nota preventiva.

**Plan:** al integrar archivos o correo, poner un adaptador entre la respuesta cruda del servicio y
el vocabulario del dominio.

## Resumen

| # | Violación | Severidad | Acción | Estado |
|---|---|---|---|---|
| V1 | `calificacion` dentro de `documentos` | Alta | Extraer colección y servicio propios (ADR 0003) | Abierta, con plan |
| V2 | `autor` como texto libre | Media | Migrar a `autor_id` cuando exista `usuarios` | Abierta, preventiva |
| V3 | `administracion` sin historial ni identidad | Baja hoy | Regla de interfaz + persistencia futura | Regla documentada |
| V4 | Sin capa anticorrupción para archivos/correo | Baja | Adaptador al integrar | Nota preventiva |

Ninguna de estas violaciones se presenta como resuelta: las que requieren un corte nuevo están
abiertas con su ADR o su plan.
