from models import Carpeta, Usuario, db


def test_ruta_principal_sin_autenticacion(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200


def test_ruta_principal_con_autenticacion(cliente_autenticado):
    respuesta = cliente_autenticado.get("/")
    assert respuesta.status_code == 200


def test_navegacion_carpeta(cliente_autenticado, usuario, app):
    with app.app_context():
        folder = Carpeta(nombre="Carpeta de Navegación", usuario_id=usuario.id)
        db.session.add(folder)
        db.session.commit()
        folder_id = folder.id
        assert Carpeta.query.get(folder_id) is not None

    respuesta = cliente_autenticado.get(f"/?carpeta_id={folder_id}")
    assert respuesta.status_code in [200, 404]


def test_acceso_carpeta_otro_usuario(cliente_autenticado, app):
    with app.app_context():
        otro_usuario = Usuario(nombre="Otro Usuario", correo="otro2@example.com")
        otro_usuario.codificar_contrasena("contrasena123")
        db.session.add(otro_usuario)
        db.session.commit()
        otro_usuario_id = otro_usuario.id

        otra_carpeta = Carpeta(nombre="Otra", usuario_id=otro_usuario_id)
        db.session.add(otra_carpeta)
        db.session.commit()
        folder_id = otra_carpeta.id

    respuesta = cliente_autenticado.get(f"/?carpeta_id={folder_id}")
    assert respuesta.status_code in [403, 404]
