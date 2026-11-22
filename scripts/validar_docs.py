#!/usr/bin/env python
"""Validación automática de la documentación de ShareU (S16/S17).

Comprueba lo que la ficha del proyecto final exige y que un revisor humano
tendría que revisar a mano:

1. rutas mínimas del contrato (arc42 1–12, ADR, C4 1–3, aspectos, IA, README);
2. nombres de ADR según `NNNN-titulo-en-kebab-case.md`;
3. enlaces locales de Markdown que resuelven a un archivo existente;
4. tabla de aspectos con las ocho columnas y evidencia navegable;
5. ausencia de marcadores de plantilla (`TODO`, `TBD`, lorem ipsum…).

Uso:
    python scripts/validar_docs.py
    python scripts/validar_docs.py --verbose

Sale con código 1 si encuentra cualquier error. No necesita red ni credenciales.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

RAIZ = Path(__file__).resolve().parents[1]
DOCS = RAIZ / "docs"

RUTAS_OBLIGATORIAS = [
    RAIZ / "README.md",
    DOCS / "aspectos.md",
    DOCS / "ia.md",
    DOCS / "api" / "openapi.yaml",
    DOCS / "arc42" / "00-portada.md",
    DOCS / "c4" / "nivel1.mmd",
    DOCS / "c4" / "nivel2.mmd",
    DOCS / "c4" / "nivel3.mmd",
    DOCS / "c4" / "nivel-2.md",
    DOCS / "c4" / "nivel-3.md",
]

PATRON_ADR = re.compile(r"^\d{4}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
PATRON_ENLACE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
PATRON_PLANTILLA = re.compile(r"\bTODO\b|\bTBD\b|\bFIXME\b|lorem ipsum|arc42 template")
PATRON_FILA_ASPECTO = re.compile(r"^\|\s*(A\d+)\s*\|")
ESQUEMAS_EXTERNOS = ("http://", "https://", "mailto:", "tel:", "data:")


def _archivos_markdown() -> list[Path]:
    return sorted(
        [RAIZ / "README.md", *DOCS.rglob("*.md")],
        key=lambda ruta: ruta.as_posix(),
    )


def _sin_bloques_de_codigo(texto: str) -> list[tuple[int, str]]:
    """Devuelve (número de línea, texto) fuera de bloques ```...```."""
    lineas: list[tuple[int, str]] = []
    dentro = False
    for numero, linea in enumerate(texto.splitlines(), start=1):
        if linea.lstrip().startswith("```"):
            dentro = not dentro
            continue
        if not dentro:
            lineas.append((numero, linea))
    return lineas


def _destino_enlace(origen: Path, destino: str) -> Path | None:
    limpio = unquote(destino.strip().strip("<>").split("#", 1)[0])
    if not limpio or limpio.startswith(ESQUEMAS_EXTERNOS):
        return None
    if limpio.startswith("/"):
        return RAIZ / limpio.lstrip("/")
    return (origen.parent / limpio).resolve()


def comprobar_rutas() -> list[str]:
    errores: list[str] = []
    for ruta in RUTAS_OBLIGATORIAS:
        if not ruta.exists():
            errores.append(f"Falta la ruta obligatoria: {ruta.relative_to(RAIZ)}")
    for numero in range(1, 13):
        coincidencias = list((DOCS / "arc42").glob(f"{numero:02d}-*.md"))
        if not coincidencias:
            errores.append(f"Falta la sección {numero:02d} de arc42 en docs/arc42/")
    return errores


def comprobar_adr() -> list[str]:
    errores: list[str] = []
    for ruta in sorted((DOCS / "adr").glob("*.md")):
        if not PATRON_ADR.match(ruta.name):
            errores.append(f"ADR con nombre fuera de convención: {ruta.name}")
    return errores


def comprobar_enlaces() -> tuple[list[str], int]:
    errores: list[str] = []
    revisados = 0
    for archivo in _archivos_markdown():
        texto = archivo.read_text(encoding="utf-8")
        for numero, linea in _sin_bloques_de_codigo(texto):
            for destino in PATRON_ENLACE.findall(linea):
                destino_path = _destino_enlace(archivo, destino)
                if destino_path is None:
                    continue
                revisados += 1
                if not destino_path.exists():
                    relativo = archivo.relative_to(RAIZ).as_posix()
                    errores.append(
                        f"Enlace roto en {relativo}:{numero}: {destino}"
                    )
    return errores, revisados


def comprobar_aspectos() -> tuple[list[str], int]:
    errores: list[str] = []
    ruta = DOCS / "aspectos.md"
    filas = 0
    for numero, linea in _sin_bloques_de_codigo(ruta.read_text(encoding="utf-8")):
        coincidencia = PATRON_FILA_ASPECTO.match(linea)
        if not coincidencia:
            continue
        filas += 1
        celdas = [celda.strip() for celda in linea.strip().strip("|").split("|")]
        if len(celdas) != 8:
            errores.append(
                f"Fila {coincidencia.group(1)} con {len(celdas)} columnas (se esperan 8)"
            )
            continue
        for indice, nombre in ((3, "C4"), (4, "ADR"), (5, "Código"), (6, "Pruebas"), (7, "Evidencia")):
            if "`" not in celdas[indice] and "](" not in celdas[indice]:
                errores.append(
                    f"Fila {coincidencia.group(1)}: la columna {nombre} no es navegable"
                )
    if filas < 10:
        errores.append(f"La tabla de aspectos solo tiene {filas} filas (se esperan 10)")
    return errores, filas


def comprobar_plantillas() -> list[str]:
    errores: list[str] = []
    for archivo in _archivos_markdown():
        for numero, linea in _sin_bloques_de_codigo(archivo.read_text(encoding="utf-8")):
            if PATRON_PLANTILLA.search(linea):
                relativo = archivo.relative_to(RAIZ).as_posix()
                errores.append(f"Marcador de plantilla en {relativo}:{numero}: {linea.strip()[:80]}")
    return errores


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    errores: list[str] = []
    errores.extend(comprobar_rutas())
    errores.extend(comprobar_adr())
    errores_enlaces, enlaces = comprobar_enlaces()
    errores.extend(errores_enlaces)
    errores_aspectos, filas = comprobar_aspectos()
    errores.extend(errores_aspectos)
    errores.extend(comprobar_plantillas())

    if args.verbose:
        print(f"Enlaces locales revisados: {enlaces}")
        print(f"Filas de aspectos revisadas: {filas}")
        print(f"ADRs revisados: {len(list((DOCS / 'adr').glob('*.md')))}")

    if errores:
        print(f"Validación de documentación: {len(errores)} error(es)")
        for error in errores:
            print(f"  - {error}")
        return 1

    print(
        "Validación de documentación: OK "
        f"({enlaces} enlaces, {filas} filas de aspectos, "
        f"{len(list((DOCS / 'adr').glob('*.md')))} ADR)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
