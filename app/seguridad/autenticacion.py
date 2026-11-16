"""Componente de seguridad compartido: autorización de operaciones de escritura.

No es un módulo de dominio: es infraestructura transversal (como el logging) y
por eso cualquier módulo puede importarlo. La decisión está en el ADR 0014.

Mientras el módulo `usuarios` no implemente autenticación completa, toda
escritura exige la credencial administrativa `SHAREU_ADMIN_TOKEN`, comparada en
tiempo constante. Si la variable no está configurada, la escritura se apaga en
lugar de quedar abierta por omisión (fail-closed).
"""
from __future__ import annotations

import os
import secrets

from fastapi import HTTPException, status


def exigir_token_admin(x_admin_token: str | None) -> None:
    """Autoriza una escritura con `X-Admin-Token`.

    - 503 si el despliegue no configuró `SHAREU_ADMIN_TOKEN` (fail-closed).
    - 401 si el token falta o no coincide.
    """
    esperado = os.getenv("SHAREU_ADMIN_TOKEN")
    if not esperado:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La escritura está deshabilitada: falta SHAREU_ADMIN_TOKEN",
        )
    if not secrets.compare_digest(x_admin_token or "", esperado):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credencial administrativa inválida",
        )
