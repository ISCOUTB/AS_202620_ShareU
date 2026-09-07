# AS_202620_ShareU

ShareU es una plataforma web para compartir y encontrar material académico
organizado por universidad, carrera y materia.

## Problema

Los estudiantes suelen perder tiempo buscando apuntes, ejercicios, talleres,
parciales y otros materiales en diferentes medios.

## Arquitectura

ShareU utiliza un **monolito modular**: un único desplegable organizado por
dominios.

- `usuarios`: registro, autenticación y perfil.
- `documentos`: clasificación y persistencia de material académico.
- `busqueda`: búsqueda, filtros y ordenamiento de resultados.
- `calificaciones`: valoración de documentos.
- `administracion`: reportes y moderación.

La decisión está documentada en
[`docs/adr/0001-estilo-arquitectonico.md`](docs/adr/0001-estilo-arquitectonico.md)
y se relaciona con el escenario de usabilidad de
[`docs/aspectos/aspectos.md`](docs/aspectos/aspectos.md).

## Requisitos

- Python 3.10 o superior.
- `pip`.

## Instalación

```bash
git clone https://github.com/ISCOUTB/AS_202620_ShareU.git
cd AS_202620_ShareU
```

Crear y activar un entorno virtual:

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`.

Documentación interactiva: `http://127.0.0.1:8000/docs`.

## Corte vertical de búsqueda

El recorrido funcional implementado consulta documentos persistidos en SQLite y
permite combinar los filtros en una sola solicitud:

```text
GET /busqueda/documentos
```

Filtros disponibles:

- `universidad`
- `carrera`
- `materia`
- `tipo`
- `palabra_clave`
- `min_calificacion`

Ejemplo:

```bash
curl "http://127.0.0.1:8000/busqueda/documentos?materia=Programación"
```

La respuesta contiene el total y los resultados con título, universidad,
carrera, materia, tipo, autor y calificación.

## Verificación

Endpoint de salud:

```bash
curl http://127.0.0.1:8000/health
```

Respuesta esperada:

```json
{"estado": "ok"}
```

Los cinco módulos conservan un endpoint de verificación:

- `/usuarios/ping`
- `/documentos/ping`
- `/busqueda/ping`
- `/calificaciones/ping`
- `/administracion/ping`

## Pruebas

```bash
pytest -q
```

El workflow de GitHub Actions en
[`.github/workflows/tests.yml`](.github/workflows/tests.yml) ejecuta estas
pruebas automáticamente en cada `push` y `pull_request`.

## Documentación

- [arc42](docs/arc42/arc42.md)
- [C4 nivel 1](docs/c4/nivel1.mmd)
- [C4 nivel 2](docs/c4/nivel-2.md) — [diagrama editable](docs/c4/nivel2.mmd)
- [ADR 0001](docs/adr/0001-estilo-arquitectonico.md)
- [Aspectos de calidad](docs/aspectos/aspectos.md)
- [Uso de IA](docs/ia.md)
