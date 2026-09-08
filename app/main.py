"""Punto de entrada de ShareU.

Monolito modular: cada dominio (usuarios, documentos, busqueda,
calificaciones, administracion) se monta como un router independiente.
Ningún módulo importa el modelo interno de otro (ver docs/adr/0001).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.usuarios.router import router as usuarios_router
from app.documentos.router import router as documentos_router
from app.busqueda.router import router as busqueda_router
from app.calificaciones.router import router as calificaciones_router
from app.administracion.router import router as administracion_router

app = FastAPI(title="ShareU")

# Permite probar el frontend estático contra el backend local sin introducir
# dependencias externas. En producción, este origen debe restringirse.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"]
)

app.include_router(usuarios_router)
app.include_router(documentos_router)
app.include_router(busqueda_router)
app.include_router(calificaciones_router)
app.include_router(administracion_router)


@app.get("/health")
def health() -> dict:
    return {"estado": "ok"}
