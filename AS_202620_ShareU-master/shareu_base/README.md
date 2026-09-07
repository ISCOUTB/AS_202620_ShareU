# Esqueleto base — monolito modular (FastAPI)

Estructura base replicando el patrón de ISCOUTB/AS_202620_ShareU:
un monolito modular donde cada dominio vive en su propia carpeta bajo
`app/`, con su propio router y, cuando corresponde, `service.py`
(interfaz pública) y `repository.py` (persistencia).

## Estructura

```
app/
├── main.py                 # arma la app y monta cada router
├── usuarios/router.py
├── documentos/
│   ├── router.py
│   ├── service.py          # interfaz pública del módulo
│   └── repository.py       # persistencia (SQLite)
├── busqueda/
│   ├── router.py
│   └── service.py          # consume documentos.service, no su repository
├── calificaciones/router.py
└── administracion/router.py
tests/
docs/adr/0001-estilo-arquitectonico.md
requirements.txt
```

## Regla de oro
Ningún módulo accede al `repository.py` de otro módulo. Toda
comunicación entre módulos pasa por el `service.py` (interfaz pública)
del módulo dueño de los datos — así se evita el acoplamiento típico
de un monolito no modular.

## Arranque

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Verificar:
- `GET /health` → `{"estado": "ok"}`
- `GET /<modulo>/ping` → confirma que cada módulo está montado
- `GET /busqueda/documentos` → corte vertical: busqueda → documentos → repository

## Tests

```bash
pytest
```

## Presentar con Go Live

`frontend/` es un sitio estático (HTML/CSS/JS) pensado para abrirse con la
extensión **Go Live** de VS Code — Go Live no ejecuta Python, así que el
backend FastAPI y el frontend estático se presentan por separado:

1. En VS Code, clic derecho sobre `frontend/index.html` → **Open with Live Server**.
2. Por defecto arranca en **modo ejemplo**: usa datos de muestra ya
   incluidos en `script.js`, sin necesitar el backend corriendo. Sirve para
   presentar la interfaz aunque no tengas uvicorn levantado.
3. Si además quieres mostrar el backend real funcionando:
   ```bash
   uvicorn app.main:app --reload
   ```
   y luego pulsa el botón **"modo: ejemplo"** en la esquina superior derecha
   de la página — cambia a **"modo: backend real"** y trae los datos desde
   `/busqueda/documentos`. Los puntos junto a cada módulo (usuarios,
   documentos, busqueda, calificaciones, administracion) se ponen en verde
   si ese router responde y en rojo si no.
