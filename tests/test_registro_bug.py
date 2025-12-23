from models import Usuario, db


def test_registro_no_auto_login(cliente, app):
    with app.app_context():
        u = Usuario.query.filter_by(correo="test_registro@example.com").first()
        if u:
            db.session.delete(u)
            db.session.commit()

    respuesta = cliente.post(
        "/registro",
        json={"nombre": "Usuario Prueba", "correo": "test_registro@example.com", "contrasena": "contrasena123"},
    )
    assert respuesta.status_code == 200

    with app.app_context():
        usuario_db = Usuario.query.filter_by(correo="test_registro@example.com").first()
        assert usuario_db is not None
        assert usuario_db.activo is False

    res_indice = cliente.get("/")
    assert b'data-authenticated="false"' in res_indice.data


def test_login_solo_si_activo(cliente, app):
    with app.app_context():
        u = Usuario.query.filter_by(correo="test_inactivo@example.com").first()
        if not u:
            u = Usuario(nombre="Inactivo", correo="test_inactivo@example.com")
            u.codificar_contrasena("contrasena123")
            u.activo = False
            db.session.add(u)
            db.session.commit()

    respuesta = cliente.post(
        "/inicio_sesion", json={"correo": "test_inactivo@example.com", "contrasena": "contrasena123"}
    )
    assert respuesta.status_code == 401
    assert b"El usuario no esta activado" in respuesta.data
