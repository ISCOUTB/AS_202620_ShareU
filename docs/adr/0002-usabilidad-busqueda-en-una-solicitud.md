# ADR 0002: Búsqueda combinada en una sola solicitud

- **Estado:** Aceptado
- **Fecha:** septiembre de 2026
- **Aspecto relacionado:** Usabilidad

## Contexto

El escenario de calidad de ShareU establece que un estudiante debe encontrar
material relevante en **3 interacciones o menos**. La búsqueda es el flujo más
importante para lograrlo. La interfaz necesita permitir combinar palabra clave,
universidad, carrera, materia y tipo sin obligar al usuario a recorrer pantallas
adicionales.

La implementación anterior aplicaba filtros principalmente en el navegador y
no hacía explícita la medición del costo de interacción. Además, el endpoint del
backend ya permitía combinar los criterios, pero la interfaz no exponía todos los
filtros en un único flujo.

## Restricción / diagnóstico

La restricción es el presupuesto de interacción: **máximo 3 interacciones** para
realizar una búsqueda filtrada. La solución debe mantener el flujo simple y
reproducible sin introducir infraestructura adicional.

## Alternativas

### A. Mantener filtros independientes y navegación por pantallas — descartada

- Ventaja: interfaz simple por pantalla.
- Desventaja: aumenta las interacciones y rompe el presupuesto de 3.
- Consecuencia: no satisface de forma directa el escenario de calidad.

### B. Filtrado únicamente en el frontend — descartada como solución principal

- Ventaja: respuesta inmediata con los datos ya cargados.
- Desventaja: duplica reglas y no aprovecha el endpoint de búsqueda del dominio.
- Consecuencia: mayor riesgo de divergencia entre frontend y backend.

### C. Formulario único con filtros combinables y una solicitud — elegida

- Ventaja: todos los criterios están disponibles en la misma vista y se envían
  juntos al endpoint de búsqueda.
- Ventaja: la cantidad de solicitudes para una búsqueda es 1.
- Ventaja: conserva las fronteras del monolito modular.
- Consecuencia: la interfaz debe mantener sincronizados sus filtros con el
  contrato del endpoint.

## Decisión

Se adopta la alternativa C. La interfaz presenta palabra clave, universidad,
carrera, materia y tipo en el mismo formulario. El envío del formulario produce
una única solicitud `GET /busqueda/documentos` con los criterios seleccionados.

El backend aplica todos los filtros y ordena los resultados por calificación.

## Medición

- **Métrica:** número de solicitudes HTTP necesarias para ejecutar una búsqueda
  filtrada desde el formulario.
- **Línea base:** el endpoint existente soportaba filtros combinados, pero la
  interfaz no exponía todos los criterios en un único formulario y la evidencia
  no registraba esta métrica explícitamente.
- **Umbral:** ≤ 3 interacciones del usuario para completar la búsqueda.
- **Resultado de la implementación:** 1 envío del formulario → 1 solicitud HTTP
  al endpoint de búsqueda cuando el backend está activo.

La prueba automatizada `test_busqueda_combina_filtros` verifica que varios
criterios se acepten en una misma solicitud.

## Consecuencias

### Positivas

- Menor costo de interacción para el flujo principal.
- Contrato de búsqueda centralizado en el backend.
- Prueba automatizada de filtros combinados.
- No requiere infraestructura externa.

### Negativas

- El formulario contiene más controles visibles.
- Se requiere mantener el contrato de parámetros entre frontend y backend.
- La métrica HTTP no sustituye una prueba con usuarios reales; esta última debe
  realizarse si la asignatura exige evidencia empírica de usabilidad.

## Trazabilidad

`docs/aspectos/aspectos.md` → este ADR → `app/frontend/` +
`app/busqueda/` → `tests/test_busqueda.py` →
`docs/evidencia/medicion-usabilidad.md`.
