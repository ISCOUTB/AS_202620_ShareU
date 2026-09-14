# Auditoría de modularidad — violaciones y plan de corrección — Semana 6

Método: revisión manual de imports entre módulos (`app/*/service.py`,
`app/*/repository.py`, `app/*/router.py`) y de las columnas de la única
tabla existente (`documentos`), contrastadas con el lenguaje de dominio de
`docs/aspectos/aspectos.md` y `docs/arc42/arc42.md`.

## V1 — "Calificación" mezclada dentro del contexto Documentos

**Dónde:** `app/documentos/repository.py`, columna `calificacion` de la
tabla `documentos`.

**Qué pasa:** el valor es un dato semilla estático que se inserta una sola
vez junto con el resto del documento. No existe módulo `calificaciones` con
tabla propia; el que existe (`app/calificaciones/router.py`) solo responde
`/ping`. Todo el sistema (incluido `busqueda.service`, que ordena resultados
por `-documento["calificacion"]`) trata la calificación como si fuera un
atributo fijo del documento, no como el resultado de valoraciones de
estudiantes.

**Por qué es una violación de límites (no solo un TODO):** el nombre
"calificación" ya aparece en `docs/aspectos/aspectos.md` con el significado
de "valoración de documentos por parte de los usuarios", y en
`docs/arc42/arc42.md` el módulo `calificaciones` se describe como
responsable de esa valoración. El código actual usa la misma palabra para
otra cosa. Si mañana se implementa el módulo `calificaciones` con su propia
tabla sin corregir esto antes, habrá dos fuentes de verdad para "la
calificación de un documento": la columna estática en `documentos` y el
promedio calculado en `calificaciones`. Ese es precisamente el error que
esta semana pide detectar.

**Severidad:** alta — determina si el módulo `calificaciones` se puede
implementar sin invadir la tabla de `documentos`.

**Plan de corrección:**

1. Crear `app/calificaciones/repository.py` con tabla propia
   `calificaciones(id, documento_id, usuario_id, puntaje, comentario, fecha)`.
2. `app/calificaciones/service.py` expone `registrar_calificacion(...)` y
   `obtener_promedio(documento_id)`.
3. Quitar la columna `calificacion` de la interfaz pública de
   `documentos.service.obtener_documentos()` (puede quedar en la tabla como
   dato heredado hasta migrar, pero deja de exponerse como el valor
   "oficial").
4. `busqueda.service.buscar_documentos()` combina
   `documentos.service.obtener_documentos()` con
   `calificaciones.service.obtener_promedio(id)` para armar cada resultado
   y ordenar.
5. Actualizar `tests/test_busqueda.py`, que hoy asume que `calificacion`
   viene de `documentos`.
6. Registrar el cambio de frontera en
   [`docs/adr/0003-separacion-contexto-calificaciones.md`](../adr/0003-separacion-contexto-calificaciones.md)
   (ya redactado como borrador) y actualizar `docs/arc42/arc42.md` sección 8
   y el C4 correspondiente.

## V2 — "Autor" como texto libre en vez de referencia a Usuarios

**Dónde:** `app/documentos/repository.py`, columna `autor` (`"Ana"`,
`"Carlos"`, etc.).

**Qué pasa:** el nombre del autor se guarda como cadena suelta dentro de
`documentos`, sin ninguna referencia al contexto `usuarios` (que todavía no
existe, pero está previsto en el ADR 0001).

**Por qué es una violación:** es una duplicación temprana de identidad.
Cuando `usuarios` se implemente, "quién publicó el documento" pasará a
tener dos representaciones que pueden divergir (el nombre guardado en
`documentos` y el perfil real en `usuarios`) — es el mismo patrón de riesgo
que "dos escritores para el mismo dato", solo que aquí es "dos
*representaciones* del mismo dato".

**Severidad:** media — no rompe nada hoy porque `usuarios` no existe, pero
se vuelve costoso de corregir cuanto más se llene la tabla `documentos` con
autores como texto libre.

**Plan de corrección:** al implementar `usuarios`, agregar `autor_id`
(referencia) en `documentos` y tratar el nombre desnormalizado, si se
conserva, como caché de lectura — nunca como fuente de verdad.

## V3 — Usuarios y Administración sin implementación real

**Dónde:** `app/usuarios/router.py`, `app/administracion/router.py` (solo
`/ping`).

**Qué pasa:** todavía no hay datos ni lógica, por lo que hoy no hay
violación de doble escritor.

**Por qué se documenta igual:** es el riesgo más probable a futuro.
`administracion` necesitará actuar sobre documentos y usuarios (retirar
contenido, suspender cuentas). Si esa implementación se hace escribiendo
directamente en las tablas de `documentos`/`usuarios` "porque es más
rápido", se reproduce exactamente el antipatrón de esta semana.

**Severidad:** baja hoy, alta si no se deja la regla escrita antes de
implementar.

**Plan de corrección (preventivo):** cuando se implemente
`administracion`, debe invocar operaciones expuestas por
`documentos.service`/`usuarios.service` (p. ej. `retirar_documento(id)`,
`suspender_usuario(id)`) en vez de tocar sus repositorios. Dejar esta regla
explícita en el ADR 0001 (sección "Reglas de implementación") o en un ADR
nuevo si se documenta con más detalle.

## V4 — Ausencia de capa anticorrupción para servicios externos futuros

**Dónde:** `docs/c4/nivel1.mmd` y `docs/c4/nivel2.mmd` — "Almacenamiento de
archivos" y "Servicio de correo" están definidos como sistemas externos
pero no implementados.

**Qué pasa:** todavía no hay código que los integre, así que no hay
filtración de modelos ajenos que auditar.

**Severidad:** baja por ahora — es una nota para el momento de integrarlos,
no una corrección pendiente.

**Plan:** cuando se integren, poner un adaptador (capa anticorrupción)
entre la respuesta cruda de esos servicios y el vocabulario propio de
`documentos`/`usuarios`, en vez de dejar que sus tipos aparezcan dentro del
dominio.

## Resumen

| # | Violación | Severidad | Acción |
|---|---|---|---|
| V1 | `calificacion` vive dentro de `documentos`, sin módulo `calificaciones` real | Alta | Extraer tabla y servicio propios (ADR 0003) |
| V2 | `autor` como texto libre, no referencia a `usuarios` | Media | Migrar a `autor_id` cuando exista `usuarios` |
| V3 | `usuarios`/`administracion` sin implementación — riesgo de escritura directa futura | Baja (preventiva) | Fijar la regla de invocar por interfaz antes de implementar |
| V4 | Sin capa anticorrupción para almacenamiento/correo | Baja (aún no aplica) | Planear adaptador al integrar |
