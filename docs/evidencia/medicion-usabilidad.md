# Evidencia de medición — usabilidad de búsqueda

## Objetivo

Comprobar de forma reproducible que el flujo principal de búsqueda permite
combinar criterios sin superar el presupuesto de interacción definido para
ShareU.

## Métrica

**Número de solicitudes HTTP necesarias para una búsqueda filtrada.**

Esta métrica es un indicador técnico del flujo; no debe presentarse como una
prueba de usuarios reales.

| Elemento | Valor |
|---|---|
| Línea base documental | Los filtros estaban disponibles de forma parcial en la interfaz y no existía una medición explícita del flujo. |
| Umbral de calidad | ≤ 3 interacciones del usuario |
| Implementación | Formulario único con palabra clave, universidad, carrera, materia y tipo |
| Resultado técnico | 1 envío del formulario → 1 solicitud HTTP al endpoint de búsqueda |
| Prueba automatizada | `test_busqueda_combina_filtros` |

## Cómo reproducir

1. Iniciar el backend con `uvicorn app.main:app --reload`.
2. Abrir `app/frontend/index.html` desde un servidor estático local.
3. Seleccionar cualquier combinación de filtros.
4. Presionar **Buscar** una vez.
5. Verificar en las herramientas de red del navegador que la búsqueda genera
   una única solicitud a `GET /busqueda/documentos`.

## Alcance de la evidencia

El resultado de 1 solicitud verifica el diseño técnico del flujo. Para afirmar
una medida de usabilidad con estudiantes sería necesario ejecutar una prueba
con participantes y registrar el número real de interacciones. Esa evidencia
no se inventa ni se sustituye por la prueba automatizada.
