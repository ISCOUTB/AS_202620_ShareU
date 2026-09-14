# Aspectos de calidad

## Idea del proyecto

ShareU es una plataforma web para estudiantes universitarios. Permite compartir
y encontrar apuntes, ejercicios, talleres, parciales y otros documentos
organizados por universidad, carrera y materia.

## Aspecto prioritario: Usabilidad

La usabilidad es el aspecto de calidad prioritario porque el valor principal de
ShareU depende de que un estudiante pueda encontrar material académico de forma
ágil.

### Escenario de calidad

| Elemento | Descripción |
|---|---|
| **Fuente del estímulo** | Un estudiante universitario que utiliza ShareU |
| **Estímulo** | El estudiante necesita encontrar material académico específico y combina criterios de búsqueda |
| **Artefacto** | Interfaz y módulo de búsqueda |
| **Entorno** | Uso normal desde computador o celular |
| **Respuesta** | El sistema permite combinar palabra clave, universidad, carrera, materia y tipo en un único flujo |
| **Medida de respuesta** | El flujo debe completarse en **3 interacciones o menos**; técnicamente, la búsqueda combinada se resuelve con una solicitud HTTP |

### Restricción identificada

El presupuesto de interacción limita el flujo principal a tres interacciones. Por
eso se evita obligar al estudiante a navegar entre pantallas o aplicar filtros
por separado.

### Tácticas

- Filtros visibles en la misma vista de resultados.
- Palabra clave y filtros combinables en un único formulario.
- Un solo envío para transmitir todos los criterios al backend.
- Información clave visible en cada resultado: título, materia, tipo, autor y
  calificación.
- Mensajes claros cuando no existen resultados.

### Verificación

La prueba automatizada `test_busqueda_combina_filtros` comprueba que varios
criterios se aceptan en una única solicitud. La evidencia técnica de la métrica
se documenta en [`docs/evidencia/medicion-usabilidad.md`](../evidencia/medicion-usabilidad.md).

La métrica técnica no sustituye una prueba de usuarios reales; si la rúbrica
exige participantes, esa actividad debe ejecutarse y anexarse como evidencia.

## Trazabilidad

| Requisito / restricción | Aspecto | ADR | Código | Prueba | Evidencia |
|---|---|---|---|---|---|
| ≤ 3 interacciones | Usabilidad | [ADR 0002](https://github.com/ISCOUTB/AS_202620_ShareU/blob/b7737be88997143da3d03acdec6d9c3419c402f4/docs/adr/0002-usabilidad-busqueda-en-una-solicitud.md) | [`app/frontend/`](https://github.com/ISCOUTB/AS_202620_ShareU/tree/b7737be88997143da3d03acdec6d9c3419c402f4/app/frontend), [`app/busqueda/`](https://github.com/ISCOUTB/AS_202620_ShareU/tree/b7737be88997143da3d03acdec6d9c3419c402f4/app/busqueda) | [`test_busqueda_combina_filtros`](https://github.com/ISCOUTB/AS_202620_ShareU/blob/b7737be88997143da3d03acdec6d9c3419c402f4/tests/test_busqueda.py#L36-L50) | [`medicion-usabilidad.md`](https://github.com/ISCOUTB/AS_202620_ShareU/blob/b7737be88997143da3d03acdec6d9c3419c402f4/docs/evidencia/medicion-usabilidad.md) |
| Arquitectura por dominios | Modificabilidad / simplicidad | [ADR 0001](https://github.com/ISCOUTB/AS_202620_ShareU/blob/b7737be88997143da3d03acdec6d9c3419c402f4/docs/adr/0001-estilo-arquitectonico.md) | [`app/*`](https://github.com/ISCOUTB/AS_202620_ShareU/tree/b7737be88997143da3d03acdec6d9c3419c402f4/app) | [`tests/test_esqueleto.py`](https://github.com/ISCOUTB/AS_202620_ShareU/blob/b7737be88997143da3d03acdec6d9c3419c402f4/tests/test_esqueleto.py) | [ADR 0001](https://github.com/ISCOUTB/AS_202620_ShareU/blob/b7737be88997143da3d03acdec6d9c3419c402f4/docs/adr/0001-estilo-arquitectonico.md) |

## Decisión arquitectónica relacionada

El escenario de usabilidad también motiva el uso de un **monolito modular**. La
búsqueda permanece como un módulo de dominio independiente, lo que permite
evolucionar el flujo sin mezclar sus reglas con calificaciones,
administración o usuarios.
