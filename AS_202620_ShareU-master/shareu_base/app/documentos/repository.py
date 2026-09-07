"""Persistencia del módulo documentos usando SQLite.

El repositorio es propiedad de este módulo. Otros módulos consumen
su interfaz de servicio y no acceden directamente a estas tablas.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB = BASE_DIR / "data" / "app.db"


def _db_path() -> Path:
    return Path(os.getenv("APP_DB_PATH", DEFAULT_DB))


def _connect() -> sqlite3.Connection:
    path = _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection


def _initialize(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL
        )
        """
    )
    connection.commit()


def listar_documentos() -> list[dict[str, Any]]:
    with _connect() as connection:
        _initialize(connection)
        rows = connection.execute(
            "SELECT id, titulo, autor FROM documentos ORDER BY id"
        ).fetchall()
    return [dict(row) for row in rows]
