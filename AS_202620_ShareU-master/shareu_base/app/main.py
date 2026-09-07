"""Punto de entrada de la aplicación.

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

app = FastAPI(title="MiApp")

# Permite que el frontend estático servido por Go Live (u otro puerto
# distinto al de uvicorn) pueda llamar a esta API durante la demo.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios_router)
app.include_router(documentos_router)
app.include_router(busqueda_router)
app.include_router(calificaciones_router)
app.include_router(administracion_router)


@app.get("/health")
def health() -> dict:
    return {"estado": "ok"}
