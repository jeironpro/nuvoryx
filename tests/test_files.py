"""
Tests para operaciones con archivos y carpetas
"""
import json

import pytest

from models import Archivo, Carpeta, db


def test_crear_carpeta(auth_client, app):
    """Test crear carpeta"""
    response = auth_client.post("/crear-carpeta", data={"nombre": "Nueva Carpeta"})

    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["success"] is True
    assert data["nombre"] == "Nueva Carpeta"

    with app.app_context():
        folder = Carpeta.query.filter_by(nombre="Nueva Carpeta").first()
        assert folder is not None


def test_crear_carpeta_sin_nombre(auth_client):
    """Test crear carpeta sin nombre"""
    response = auth_client.post("/crear-carpeta", data={})

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data


def test_eliminar_carpeta(auth_client, app, carpeta):
    """Test eliminar carpeta"""
    with app.app_context():
        folder_id = carpeta.id

    response = auth_client.delete(f"/eliminar-carpeta/{folder_id}")

    assert response.status_code == 200

    with app.app_context():
        folder = Carpeta.query.get(folder_id)
        assert folder is None


def test_eliminar_archivo(auth_client, app, archivo):
    """Test eliminar archivo"""
    with app.app_context():
        file_id = archivo.id

    response = auth_client.delete(f"/eliminar/{file_id}")

    assert response.status_code == 200

    with app.app_context():
        file = Archivo.query.get(file_id)
        assert file is None


def test_usuario_ve_solo_sus_carpetas(auth_client, app, usuario):
    """Test que usuario ve solo sus carpetas"""
    with app.app_context():
        # Crear carpeta de otro usuario
        other_folder = Carpeta(nombre="Other Folder", usuario_id=999)
        db.session.add(other_folder)

        # Crear carpeta del usuario autenticado
        user_folder = Carpeta(nombre="My Folder", usuario_id=usuario.id)
        db.session.add(user_folder)
        db.session.commit()

    response = auth_client.get("/")
    assert response.status_code == 200

    # Verificar que solo ve su carpeta
    html = response.data.decode()
    assert "My Folder" in html
    assert "Other Folder" not in html
