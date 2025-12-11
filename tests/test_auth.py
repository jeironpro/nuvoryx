"""
Tests para autenticación
"""

import json

# def test_registro_exitoso(client):
#     """Test registro de usuario exitoso"""
#     response = client.post(
#         "/registro",
#         json={"nombre": "New User", "email": "newuser@example.com", "password": "password123"},
#     )

#     assert response.status_code == 200
#     data = json.loads(response.data)
#     assert data["success"] is True
#     assert data["usuario"]["nombre"] == "New User"
#     assert data["usuario"]["correo"] == "newuser@example.com"


def test_registro_email_duplicado(client, usuario):
    """Test registro con email duplicado"""
    response = client.post(
        "/registro",
        json={"nombre": "Another User", "email": usuario.correo, "password": "password123"},
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_registro_password_corto(client):
    """Test registro con contraseña corta"""
    response = client.post("/registro", json={"nombre": "User", "email": "user@example.com", "password": "123"})

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_login_exitoso(client, usuario):
    """Test login exitoso"""
    response = client.post("/inicio_sesion", json={"email": usuario.correo, "password": "testpass123"})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["usuario"]["correo"] == usuario.correo


def test_login_password_incorrecta(client, usuario):
    """Test login con contraseña incorrecta"""
    response = client.post("/inicio_sesion", json={"email": usuario.correo, "password": "wrongpassword"})

    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data


def test_login_correo_inexistente(client):
    """Test login con correo inexistente"""
    response = client.post("/inicio_sesion", json={"email": "noexiste@example.com", "password": "password123"})

    assert response.status_code == 401
    data = json.loads(response.data)
    assert "error" in data


def test_logout(auth_client):
    """Test logout"""
    response = auth_client.post("/cerrar_sesion")

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
