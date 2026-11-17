# Evidencia de medición — usabilidad de la búsqueda

## Objetivo

Comprobar de forma reproducible que el flujo principal de búsqueda permite combinar criterios sin
superar el presupuesto de interacción definido para ShareU.

## Métrica

**Número de solicitudes HTTP necesarias para una búsqueda filtrada.**

Es un indicador técnico del flujo; no es una prueba con estudiantes reales.

| Elemento | Valor |
|---|---|
| Línea base documental | No existía una medición explícita del flujo; los filtros se aplicaban por separado |
| Umbral funcional | ≤ 3 interacciones del usuario |
| Implementación | Formulario único en Next.js (`app/frontend/app/page.tsx`) con palabra clave, universidad, carrera, materia y tipo |
| Resultado técnico | 1 envío del formulario → **1 solicitud HTTP** a `GET /busqueda/documentos` |
| Prueba automatizada | `tests/test_busqueda.py::test_busqueda_combina_filtros` y `tests/test_escenario_usabilidad.py` |

Esta métrica **no** sustituye a la medición de rendimiento y costo de S10/S14 (p95, error y lecturas
por búsqueda), que es la que se contrasta con un umbral de sistema (ADR 0016).

## Cómo reproducir

1. Iniciar el backend con `uvicorn app.main:app --reload`.
2. Iniciar el frontend con `cd app/frontend && npm run dev` (o `docker compose up`).
3. Abrir <http://localhost:3000>.
4. Escribir cualquier combinación de filtros y pulsar **Buscar** una vez.
5. En las herramientas de red del navegador, verificar que se genera **una única** solicitud a
   `GET /busqueda/documentos`.

## Alcance de la evidencia

El resultado de una solicitud verifica el diseño técnico del flujo. Para afirmar una medida de
usabilidad con estudiantes haría falta una prueba con participantes y registrar el número real de
interacciones. Esa evidencia no se inventa ni se sustituye por la prueba automatizada.
