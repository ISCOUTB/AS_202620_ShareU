# Correcciones — respuesta a la revisión de semana-05-corte1

**Repositorio:** `ISCOUTB/AS_202620_ShareU`
**Revisión que se responde:** [`revisiones/2026-2/AS_202620_ShareU/semana-05-corte1.md`](https://github.com/ISCOUTB/AS_202620_feedback/blob/master/revisiones/2026-2/AS_202620_ShareU/semana-05-corte1.md)
**Fecha de esta respuesta:** septiembre de 2026

Este documento responde punto por punto a los hallazgos de la revisión definitiva
de la semana 5 (corte 1), aclara dos premisas de la ficha que no aplicaban a
nuestro equipo, y deja constancia de las correcciones que sí se hicieron sobre
el repositorio.

## 1. Sobre el reto / restricción asignada

La ficha `semana-05-corte1.md` y la revisión asumen que a cada equipo se le
asignó una restricción arquitectónica nueva para diagnosticar, decidir e
implementar en este corte. **A nuestro equipo el docente no nos asignó
ninguna restricción para este corte.** Por esa razón el repositorio no
contiene un ADR de reto, un diagnóstico de restricción ni una medición
asociada: no es una omisión del equipo, es que el insumo de entrada de esa
parte de la rúbrica nunca llegó.

Pedimos que este punto se verifique directamente con el docente antes de
mantener las filas correspondientes de la matriz («Impacto de la restricción
localizado…», «ADR del reto…», «Aplicación sobre el corte vertical…»,
«Resultado contrastado con el umbral…») como *No cumple*, ya que no cumplir
un requisito que no fue asignado no debería puntuar igual que no responder a
uno que sí se asignó.

## 2. Sobre la etiqueta `corte-1`

La revisión marca como *No cumple* que la etiqueta `corte-1` apunte a un
commit posterior al cierre. Sobre esto: **el docente indicó que, por ahora,
no se está trabajando con etiquetas** como mecanismo de entrega. La etiqueta
que existe en el repositorio quedó de pruebas o cargas anteriores y no debe
interpretarse como el mecanismo formal de cierre de este corte.

Solicitamos confirmar con el docente cuál es el estado que efectivamente
debe calificarse (¿HEAD de la rama `master` al momento del cierre?) en lugar
de la etiqueta, dado que esta última no refleja la instrucción vigente.

## 3. Estructura del repositorio (corregida)

La revisión encontró tres copias parciales del proyecto conviviendo en el
mismo árbol (`AS_202620_ShareU-master/`, un `shareu_base/` anidado dentro de
esa carpeta, y luego todo el contenido movido a `Corte_1/`), producto de
cargas de archivos ZIP por la interfaz web de GitHub.

**Esto ya se corrigió.** El repositorio quedó con una sola copia del
proyecto en la raíz (`app/`, `docs/`, `tests/`, `README.md`,
`requirements.txt`, `.github/`), sin las carpetas duplicadas
`AS_202620_ShareU-master/` ni `shareu_base/`. Se puede verificar con:

```bash
git ls-tree -r --name-only HEAD | grep -E "AS_202620_ShareU-master|shareu_base"
```

Este comando no debería devolver resultados sobre el commit vigente.

## 4. Corrección de calidad de código (SonarCloud)

Como parte del trabajo de este corte se identificaron y corrigieron **9
issues abiertos** reportados por el análisis estático de SonarCloud
(5 de Reliability, 3 de Maintainability, 1 de Security). El detalle:

| Archivo | Issue original | Corrección aplicada |
|---|---|---|
| `app/frontend/script.js` (L29, L30) | `.sort()` sin función de comparación | Se agregó `(a, b) => a.localeCompare(b)` en ambos `.sort()` |
| `app/frontend/index.html` (L30, L40, L43) | Campos de formulario sin etiqueta accesible | Se agregó `aria-label` al input de búsqueda y a los dos `<select>` |
| `app/busqueda/service.py` (L13) | Complejidad cognitiva de `buscar_documentos` en 21 (máximo permitido: 15) | Se dividió la función en predicados independientes (`_coincide_campo`, `_coincide_palabra_clave`, `_coincide_calificacion`) compuestos con `all(...)` |
| `app/documentos/repository.py` (L54) | Literal `"Ingeniería de Sistemas"` duplicado 4 veces y `"Universidad Nacional"` duplicado 3 veces | Se definieron constantes (`_INGENIERIA_SISTEMAS`, `_UNIVERSIDAD_NACIONAL`, `_UNIVERSIDAD_DEL_NORTE`) |
| `requirements.txt` (vía `tests.yml` L21) | Dependencias sin versión fija (security-sensitive) | Se fijaron versiones exactas de `fastapi`, `uvicorn`, `pytest`, `httpx` |

Tras estos cambios, el Quality Gate de SonarCloud pasó a **A en todas las
categorías** (Reliability, Maintainability, Security). Los tests existentes
en `tests/test_busqueda.py` se verificaron localmente y siguen pasando sin
cambios de comportamiento tras el refactor de `service.py`.

Este trabajo quedó registrado como entrada nueva en
[`docs/ia/ia.md`](docs/ia/ia.md), incluyendo qué se usó, qué se descartó
(hash-locking completo de dependencias) y la revisión humana aplicada
(ejecución de pruebas y verificación del Quality Gate).

## 5. Petición al docente

Solicitamos que, al recalificar este corte, se tenga en cuenta que:

1. No existió un reto/restricción asignado a este equipo para el corte 1.
2. La etiqueta no es, según instrucción del docente, el mecanismo de cierre
   vigente en esta etapa del curso.
3. La desviación de estructura (triplicación del árbol) ya fue corregida.
4. Se realizó y documentó trabajo de calidad de código (SonarCloud) sobre el
   corte vertical existente.

Quedamos atentos a cualquier evidencia adicional que se requiera para
sustentar estos puntos.
