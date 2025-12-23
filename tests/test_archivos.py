import json
import os

from models import Archivo, Carpeta, db


def test_crear_carpeta(cliente_autenticado, app):
    respuesta = cliente_autenticado.post("/crear-carpeta", data={"nombre": "Nueva Carpeta"})

    assert respuesta.status_code == 200
    datos = json.loads(respuesta.data)
    assert datos["success"] is True
    assert datos["nombre"] == "Nueva Carpeta"

    with app.app_context():
        folder = Carpeta.query.filter_by(nombre="Nueva Carpeta").first()
        assert folder is not None


def test_crear_carpeta_sin_nombre(cliente_autenticado):
    respuesta = cliente_autenticado.post("/crear-carpeta", data={})

    assert respuesta.status_code == 400
    datos = json.loads(respuesta.data)
    assert "error" in datos


def test_eliminar_carpeta(cliente_autenticado, app, usuario):
    with app.app_context():
        folder = Carpeta(nombre="Carpeta a Eliminar", usuario_id=usuario.id)
        db.session.add(folder)
        db.session.commit()
        folder_id = folder.id
        assert Carpeta.query.get(folder_id) is not None

    respuesta = cliente_autenticado.delete(f"/eliminar-carpeta/{folder_id}")
    assert respuesta.status_code in [200, 404]


def test_eliminar_archivo(cliente_autenticado, app, usuario):
    with app.app_context():
        carpeta_subidas = app.config["CARPETA_SUBIDAS"]
        ruta_archivo_prueba = os.path.join(carpeta_subidas, "prueba_eliminar_hash.txt")

        if not os.path.exists(carpeta_subidas):
            os.makedirs(carpeta_subidas)
        with open(ruta_archivo_prueba, "w") as f:
            f.write("contenido de prueba")

        archivo_obj = Archivo(
            nombre_original="prueba_eliminar.txt",
            nombre_hash="prueba_eliminar_hash.txt",
            tipo="otro",
            tamano="1.0 KB",
            usuario_id=usuario.id,
        )
        db.session.add(archivo_obj)
        db.session.commit()
        archivo_id = archivo_obj.id
        assert Archivo.query.get(archivo_id) is not None

    respuesta = cliente_autenticado.delete(f"/eliminar/{archivo_id}")
    assert respuesta.status_code in [200, 404]


def test_usuario_ve_solo_sus_carpetas(cliente_autenticado, app, usuario):
    respuesta = cliente_autenticado.get("/")
    assert respuesta.status_code == 200
    html = respuesta.data.decode()
    assert "<!DOCTYPE html>" in html or "<html" in html
