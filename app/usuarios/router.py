"""Módulo: usuarios.

Responsabilidad: registro, autenticación, administración del perfil y consulta
de documentos propios.
"""
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.usuarios import service

UNIVERSIDAD_PREDETERMINADA = "Universidad Nacional"
CARRERA_PREDETERMINADA = "Ingeniería de Sistemas"

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


class RegistroEntrada(BaseModel):
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=6, max_length=120)
    nombre: str = Field(min_length=1, max_length=120)
    universidad: str = Field(default=UNIVERSIDAD_PREDETERMINADA, max_length=120)
    carrera: str = Field(default=CARRERA_PREDETERMINADA, max_length=120)


class LoginEntrada(BaseModel):
    email: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=1, max_length=120)


class DocumentoUsuarioEntrada(BaseModel):
    titulo: str = Field(min_length=1, max_length=200)
    materia: str = Field(min_length=1, max_length=120)
    tipo: str = Field(min_length=1, max_length=60)
    universidad: str = Field(default=UNIVERSIDAD_PREDETERMINADA, max_length=120)
    carrera: str = Field(default=CARRERA_PREDETERMINADA, max_length=120)
    palabras_clave: str = Field(default="", max_length=400)


def _extraer_token(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere cabecera Authorization con formato Bearer <token>",
        )
    return authorization.split(" ", 1)[1].strip()


@router.get("/ping")
def ping() -> dict:
    return {"modulo": "usuarios", "estado": "ok"}


@router.post("/registro", status_code=status.HTTP_201_CREATED)
def registro(payload: RegistroEntrada) -> dict:
    try:
        return service.registrar_usuario(
            email=payload.email,
            password=payload.password,
            nombre=payload.nombre,
            universidad=payload.universidad,
            carrera=payload.carrera,
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))


@router.post("/login")
def login(payload: LoginEntrada) -> dict:
    try:
        return service.iniciar_sesion(email=payload.email, password=payload.password)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err))


@router.get("/perfil")
def perfil(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict:
    token = _extraer_token(authorization)
    try:
        return service.obtener_perfil_por_token(token)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err))


@router.post("/logout")
def logout(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict:
    token = _extraer_token(authorization)
    service.cerrar_sesion(token)
    return {"estado": "ok"}


@router.get("/perfil/documentos")
def documentos_propios(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict:
    token = _extraer_token(authorization)
    try:
        usuario = service.obtener_perfil_por_token(token)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err))

    docs = service.obtener_documentos_usuario(usuario["nombre"])
    return {"total": len(docs), "documentos": docs}


@router.post("/perfil/documentos", status_code=status.HTTP_201_CREATED)
def subir_documento_propio(
    payload: DocumentoUsuarioEntrada,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
) -> dict:
    token = _extraer_token(authorization)
    try:
        usuario = service.obtener_perfil_por_token(token)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(err))

    documento = service.publicar_documento_usuario(
        nombre_autor=usuario["nombre"],
        titulo=payload.titulo,
        materia=payload.materia,
        tipo=payload.tipo,
        universidad=payload.universidad or usuario.get("universidad", UNIVERSIDAD_PREDETERMINADA),
        carrera=payload.carrera or usuario.get("carrera", CARRERA_PREDETERMINADA),
        palabras_clave=payload.palabras_clave,
    )
    return documento
