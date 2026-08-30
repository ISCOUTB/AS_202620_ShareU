"""Persistencia del módulo de documentos usando SQLite.

El repositorio es propiedad del módulo documentos. Otros módulos consumen
su interfaz de servicio y no acceden directamente a estas tablas.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DB = BASE_DIR / "data" / "shareu.db"


def _db_path() -> Path:
    return Path(os.getenv("SHAREU_DB_PATH", DEFAULT_DB))


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
            universidad TEXT NOT NULL,
            carrera TEXT NOT NULL,
            materia TEXT NOT NULL,
            tipo TEXT NOT NULL,
            autor TEXT NOT NULL,
            calificacion REAL NOT NULL DEFAULT 0,
            palabras_clave TEXT NOT NULL DEFAULT ''
        )
        """
    )
    count = connection.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
    if count == 0:
        connection.executemany(
            """
            INSERT INTO documentos
            (titulo, universidad, carrera, materia, tipo, autor, calificacion, palabras_clave)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("Taller de Python", "Universidad Nacional", "Ingeniería de Sistemas",
                 "Programación", "Taller", "Ana", 4.8, "python programación funciones"),
                ("Parcial de Bases de Datos", "Universidad Nacional", "Ingeniería de Sistemas",
                 "Bases de Datos", "Parcial", "Carlos", 4.5, "sql bases datos parcial"),
                ("Apuntes de Arquitectura de Software", "Universidad Nacional",
                 "Ingeniería de Sistemas", "Arquitectura de Software", "Apuntes",
                 "María", 4.7, "arquitectura software adr c4"),
                ("Ejercicios de Cálculo", "Universidad del Norte", "Ingeniería de Sistemas",
                 "Cálculo", "Ejercicios", "Luis", 4.2, "calculo derivadas integrales"),
                ("Guía de Redes", "Universidad del Norte", "Ingeniería de Telecomunicaciones",
                 "Redes", "Guía", "Sofía", 4.6, "redes tcp ip protocolos"),
            ],
        )
    connection.commit()


def listar_documentos() -> list[dict[str, Any]]:
    with _connect() as connection:
        _initialize(connection)
        rows = connection.execute(
            """
            SELECT id, titulo, universidad, carrera, materia, tipo, autor,
                   calificacion, palabras_clave
            FROM documentos
            ORDER BY id
            """
        ).fetchall()
    return [dict(row) for row in rows]
