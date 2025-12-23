from extensiones import db
from models import Notificacion, Usuario


def test_modelo_notificacion(app):
    with app.app_context():
        usuario_db = Usuario.query.first()
        if not usuario_db:
            usuario_db = Usuario(nombre="Usuario Prueba", correo="prueba@example.com")
            usuario_db.codificar_contrasena("contrasenaprueba123")
            db.session.add(usuario_db)
            db.session.commit()

        n = Notificacion(usuario_id=usuario_db.id, mensaje="Notificación de Prueba")
        db.session.add(n)
        db.session.commit()

        assert n.id is not None
        assert n.mensaje == "Notificación de Prueba"
        assert n.leida is False


def test_api_notificaciones(cliente_autenticado):
    respuesta = cliente_autenticado.post("/notificaciones", json={"mensaje": "Prueba de API"})
    assert respuesta.status_code == 200
    assert respuesta.get_json()["success"] is True

    respuesta = cliente_autenticado.get("/notificaciones")
    assert respuesta.status_code == 200
    datos = respuesta.get_json()
    assert len(datos) >= 1
    assert datos[0]["mensaje"] == "Prueba de API"

    respuesta = cliente_autenticado.post("/notificaciones/marcar-leidas")
    assert respuesta.status_code == 200

    respuesta = cliente_autenticado.delete("/notificaciones/limpiar")
    assert respuesta.status_code == 200

    respuesta = cliente_autenticado.get("/notificaciones")
    assert respuesta.status_code == 200
    assert len(respuesta.get_json()) == 0
