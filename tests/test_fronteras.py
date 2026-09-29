"""Guardia de erosión: un módulo solo importa `service` de otro módulo.

Regla de ADR 0001 (punto 3) y docs/ddd/propiedad-datos.md: ningún módulo usa
el repositorio ni archivos internos de otro. Si el código (generado o no)
cruza esa frontera, esta prueba falla.
"""
import re
from pathlib import Path

APP = Path(__file__).resolve().parents[1] / "app"
MODULOS = ["usuarios", "documentos", "busqueda", "calificaciones", "administracion"]
IMPORT = re.compile(r"^\s*(?:from|import)\s+app\.(\w+)\.(\w+)", re.MULTILINE)


def _cruces_prohibidos() -> list[str]:
    prohibidos = []
    for modulo in MODULOS:
        for archivo in (APP / modulo).glob("*.py"):
            for otro, interno in IMPORT.findall(archivo.read_text(encoding="utf-8")):
                if otro in MODULOS and otro != modulo and interno != "service":
                    prohibidos.append(f"{archivo.relative_to(APP)} -> app.{otro}.{interno}")
    return prohibidos


def test_modulos_solo_se_hablan_por_service():
    assert _cruces_prohibidos() == []
