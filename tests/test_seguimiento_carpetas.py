import time
from datetime import datetime

from models import Archivo, Carpeta, db


def test_seguimiento_actualizacion_carpeta(cliente_autenticado, app, usuario):
    """
    Verifica que la fecha de actualización de una carpeta se actualice
    al realizar acciones dentro de ella.
    """
    # 1. Crear carpeta
    with app.app_context():
        carpeta_obj = Carpeta(nombre="Carpeta de Seguimiento", usuario_id=usuario.id)
        db.session.add(carpeta_obj)
        db.session.commit()
        folder_id = carpeta_obj.id

        # Obtener valores iniciales
        db.session.refresh(carpeta_obj)
        actualizacion_inicial = carpeta_obj.fecha_actualizacion
        creacion_inicial = carpeta_obj.fecha_creacion

    # Pequeña pausa para asegurar que el timestamp será diferente
    time.sleep(1.1)

    # 2. Subir un archivo a esa carpeta
    import io

    datos = {
        "archivos": (io.BytesIO(b"contenido de prueba"), "prueba.txt"),
        "rutas_relativas": "prueba.txt",
        "carpeta_id": str(folder_id),
    }
    respuesta = cliente_autenticado.post("/subir", data=datos, content_type="multipart/form-data")
    assert respuesta.status_code == 200

    # 3. Verificar que la fecha de actualización cambió
    with app.app_context():
        carpeta_obj = Carpeta.query.get(folder_id)
        assert carpeta_obj.fecha_actualizacion > actualizacion_inicial
        assert carpeta_obj.fecha_creacion == creacion_inicial


def test_visualizacion_tabla_carpetas(cliente_autenticado, app, usuario):
    """
    Verifica que la página de inicio devuelva las fechas formateadas.
    """
    with app.app_context():
        carpeta_obj = Carpeta(nombre="Carpeta de Visualización", usuario_id=usuario.id)
        db.session.add(carpeta_obj)
        db.session.commit()
        folder_id = carpeta_obj.id

    respuesta = cliente_autenticado.get("/")
    assert respuesta.status_code == 200
    # Verificar que el formato de fecha aparezca en el HTML
    # Buscamos el patrón YYYY-MM-DD HH:MM
    import re

    patron_fecha = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
    assert patron_fecha.search(respuesta.data.decode("utf-8"))
