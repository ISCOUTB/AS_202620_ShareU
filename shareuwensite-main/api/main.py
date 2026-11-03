"""API opcional para shareU. Firebase Auth/Firestore/Storage siguen siendo la fuente principal.
Instalar: pip install fastapi uvicorn
Ejecutar: uvicorn api.main:app --reload --port 8000
Esta API base no administra credenciales ni suplanta las reglas de Firebase.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="shareU API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "service": "shareU API"}

@app.get("/busqueda/ping")
def busqueda_ping():
    return {"ok": True, "module": "busqueda"}

@app.get("/busqueda/documentos")
def busqueda_documentos():
    # Los documentos reales se consultan desde Firebase en el frontend.
    # Este endpoint es un chequeo de API, no una base de datos paralela.
    return {"resultados": [], "source": "firebase-client"}
