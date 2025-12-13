"""
Tests para autenticación
"""

import json
from unittest.mock import patch


def test_registro_exitoso(client):
    """Test registro de usuario exitoso"""
    with patch("blueprints.autenticacion.enviar_correo_confirmacion") as mock_email:
        response = client.post(
            "/registro",
            json={"nombre": "New User", "correo": "newuser@example.com", "contrasena": "password123"},
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["success"] is True
        assert data["usuario"]["nombre"] == "New User"
        assert data["usuario"]["correo"] == "newuser@example.com"
        mock_email.assert_called_once()


def test_registro_email_duplicado(client, usuario):
    """Test registro con email duplicado"""
    response = client.post(
        "/registro",
        json={"nombre": "Another User", "correo": usuario.correo, "contrasena": "password123"},
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_registro_password_corto(client):
    """Test registro con contraseña corta"""
    response = client.post("/registro", json={"nombre": "User", "correo": "user@example.com", "contrasena": "123"})

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_login_exitoso(client, usuario):
    """Test login exitoso"""
    response = client.post("/inicio_sesion", json={"correo": usuario.correo, "contrasena": "testpass123"})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["usuario"]["correo"] == usuario.correo


def test_login_password_incorrecta(client, usuario):
    """Test login con contraseña incorrecta"""
    response = client.post("/inicio_sesion", json={"correo": usuario.correo, "contrasena": "wrongpassword"})

    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data


def test_login_correo_inexistente(client):
    """Test login con correo inexistente"""
    response = client.post("/inicio_sesion", json={"correo": "noexiste@example.com", "contrasena": "password123"})

    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data


def test_logout(auth_client):
    """Test logout"""
    response = auth_client.post("/cerrar_sesion")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
