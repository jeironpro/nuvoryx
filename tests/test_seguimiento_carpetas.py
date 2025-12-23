import io
import re
import time

from models import Carpeta, db


def test_seguimiento_actualizacion_carpeta(cliente_autenticado, app, usuario):
    with app.app_context():
        carpeta_obj = Carpeta(nombre="Carpeta de Seguimiento", usuario_id=usuario.id)
        db.session.add(carpeta_obj)
        db.session.commit()
        folder_id = carpeta_obj.id

        db.session.refresh(carpeta_obj)
        actualizacion_inicial = carpeta_obj.fecha_actualizacion
        creacion_inicial = carpeta_obj.fecha_creacion

    time.sleep(1.1)

    datos = {
        "archivos": (io.BytesIO(b"contenido de prueba"), "prueba.txt"),
        "rutas_relativas": "prueba.txt",
        "carpeta_id": str(folder_id),
    }
    respuesta = cliente_autenticado.post("/subir", data=datos, content_type="multipart/form-data")
    assert respuesta.status_code == 200

    with app.app_context():
        carpeta_obj = Carpeta.query.get(folder_id)
        assert carpeta_obj.fecha_actualizacion > actualizacion_inicial
        assert carpeta_obj.fecha_creacion == creacion_inicial


def test_visualizacion_tabla_carpetas(cliente_autenticado, app, usuario):
    with app.app_context():
        carpeta_obj = Carpeta(nombre="Carpeta de Visualización", usuario_id=usuario.id)
        db.session.add(carpeta_obj)
        db.session.commit()

    respuesta = cliente_autenticado.get("/")
    assert respuesta.status_code == 200

    patron_fecha = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
    assert patron_fecha.search(respuesta.data.decode("utf-8"))
