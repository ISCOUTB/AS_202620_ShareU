"""Pruebas del módulo usuarios: registro, login, perfil y documentos propios."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_con_usuario_semilla():
    resp = client.post(
        "/usuarios/login",
        json={"email": "ana@utb.edu.co", "password": "Password123!"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["usuario"]["nombre"] == "Ana"
    assert data["usuario"]["email"] == "ana@utb.edu.co"


def test_login_credenciales_invalidas():
    resp = client.post(
        "/usuarios/login",
        json={"email": "ana@utb.edu.co", "password": "WrongPassword"},
    )
    assert resp.status_code == 401


def test_registro_nuevo_usuario_y_acceso_a_perfil():
    nuevo_email = "estudiante.nuevo@utb.edu.co"
    resp_reg = client.post(
        "/usuarios/registro",
        json={
            "email": nuevo_email,
            "password": "MiPasswordSeguro123",
            "nombre": "Estudiante Prueba",
            "universidad": "Universidad Tecnológica de Bolívar",
            "carrera": "Ingeniería de Sistemas",
        },
    )
    assert resp_reg.status_code == 201
    assert resp_reg.json()["email"] == nuevo_email

    # Login con el usuario creado
    resp_log = client.post(
        "/usuarios/login",
        json={"email": nuevo_email, "password": "MiPasswordSeguro123"},
    )
    assert resp_log.status_code == 200
    token = resp_log.json()["token"]

    # Acceder a perfil con Bearer token
    resp_perfil = client.get(
        "/usuarios/perfil",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_perfil.status_code == 200
    assert resp_perfil.json()["nombre"] == "Estudiante Prueba"

    # Subir documento propio
    resp_doc = client.post(
        "/usuarios/perfil/documentos",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "titulo": "Resumen de Álgebra Lineal",
            "materia": "Álgebra Lineal",
            "tipo": "Resumen",
            "universidad": "Universidad Tecnológica de Bolívar",
            "carrera": "Ingeniería de Sistemas",
        },
    )
    assert resp_doc.status_code == 201
    assert resp_doc.json()["titulo"] == "Resumen de Álgebra Lineal"

    # Consultar documentos propios
    resp_mis_docs = client.get(
        "/usuarios/perfil/documentos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_mis_docs.status_code == 200
    assert resp_mis_docs.json()["total"] >= 1
    titulos = [d["titulo"] for d in resp_mis_docs.json()["documentos"]]
    assert "Resumen de Álgebra Lineal" in titulos

    # Logout
    resp_out = client.post(
        "/usuarios/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_out.status_code == 200

    # Acceder después de logout falla con 401
    resp_post_logout = client.get(
        "/usuarios/perfil",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_post_logout.status_code == 401
