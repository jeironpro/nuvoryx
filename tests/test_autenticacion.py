import json
from unittest.mock import patch


def test_registro_exitoso(cliente):
    with patch("blueprints.autenticacion.enviar_correo_confirmacion") as mock_email:
        respuesta = cliente.post(
            "/registro",
            json={"nombre": "Nuevo Usuario", "correo": "nuevo@example.com", "contrasena": "contrasena123"},
        )

        assert respuesta.status_code == 200
        datos = json.loads(respuesta.data)
        assert datos["success"] is True
        assert datos["usuario"]["nombre"] == "Nuevo Usuario"
        assert datos["usuario"]["correo"] == "nuevo@example.com"
        mock_email.assert_called_once()


def test_registro_correo_duplicado(cliente, usuario):
    respuesta = cliente.post(
        "/registro",
        json={"nombre": "Otro Usuario", "correo": usuario.correo, "contrasena": "contrasena123"},
    )

    assert respuesta.status_code == 400
    datos = json.loads(respuesta.data)
    assert "error" in datos


def test_registro_contrasena_corto(cliente):
    respuesta = cliente.post(
        "/registro", json={"nombre": "Usuario", "correo": "usuario@example.com", "contrasena": "123"}
    )

    assert respuesta.status_code == 400
    datos = json.loads(respuesta.data)
    assert "error" in datos


def test_login_exitoso(cliente, usuario):
    respuesta = cliente.post("/inicio_sesion", json={"correo": usuario.correo, "contrasena": "contrasenaprueba123"})

    assert respuesta.status_code == 200
    datos = json.loads(respuesta.data)
    assert datos["success"] is True
    assert datos["usuario"]["correo"] == usuario.correo


def test_login_contrasena_incorrecta(cliente, usuario):
    respuesta = cliente.post("/inicio_sesion", json={"correo": usuario.correo, "contrasena": "clave_erronea"})

    assert respuesta.status_code == 401
    datos = json.loads(respuesta.data)
    assert "error" in datos


def test_login_correo_inexistente(cliente):
    respuesta = cliente.post("/inicio_sesion", json={"correo": "noexiste@example.com", "contrasena": "contrasena123"})

    assert respuesta.status_code == 401
    datos = json.loads(respuesta.data)
    assert "error" in datos


def test_cerrar_sesion(cliente_autenticado):
    respuesta = cliente_autenticado.post("/cerrar_sesion")

    assert respuesta.status_code == 200
    datos = json.loads(respuesta.data)
    assert datos["success"] is True
