import pytest
from flask_login import current_user

from models import Usuario, db


def test_registro_no_auto_login(cliente, app):
    """
    Verifica que después de registrarse, el usuario NO esté autenticado
    y que su estado sea 'activo=False'.
    """
    with app.app_context():
        # Limpiar usuario de prueba si existe
        u = Usuario.query.filter_by(correo="test_registro@example.com").first()
        if u:
            db.session.delete(u)
            db.session.commit()

    # 1. Registrar usuario
    respuesta = cliente.post(
        "/registro",
        json={"nombre": "Usuario Prueba", "correo": "test_registro@example.com", "contrasena": "contrasena123"},
    )
    assert respuesta.status_code == 200

    # 2. Verificar que el usuario existe y NO está activo
    with app.app_context():
        usuario_db = Usuario.query.filter_by(correo="test_registro@example.com").first()
        assert usuario_db is not None
        assert usuario_db.activo is False

    # 3. Verificar que NO hay sesión iniciada
    res_indice = cliente.get("/")
    assert b'data-authenticated="false"' in res_indice.data


def test_login_solo_si_activo(cliente, app):
    """
    Verifica que no se pueda iniciar sesión si la cuenta no está activa.
    """
    with app.app_context():
        # Crear usuario no activo
        u = Usuario.query.filter_by(correo="test_inactivo@example.com").first()
        if not u:
            u = Usuario(nombre="Inactivo", correo="test_inactivo@example.com")
            u.codificar_contrasena("contrasena123")
            u.activo = False
            db.session.add(u)
            db.session.commit()

    # Intentar login
    respuesta = cliente.post(
        "/inicio_sesion", json={"correo": "test_inactivo@example.com", "contrasena": "contrasena123"}
    )

    # Debería fallar con 401
    assert respuesta.status_code == 401
    assert b"El usuario no esta activado" in respuesta.data
