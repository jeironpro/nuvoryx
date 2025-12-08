"""
Tests para rutas de la aplicación
"""
import pytest


def test_ruta_principal_sin_auth(client):
    """Test acceso a ruta principal sin autenticación"""
    response = client.get('/')
    assert response.status_code == 200


def test_ruta_principal_con_auth(auth_client):
    """Test acceso a ruta principal con autenticación"""
    response = auth_client.get('/')
    assert response.status_code == 200


def test_navegacion_carpeta(auth_client, carpeta, app):
    """Test navegación a carpeta"""
    with app.app_context():
        folder_id = carpeta.id
    
    response = auth_client.get(f'/?carpeta_id={folder_id}')
    assert response.status_code == 200


def test_acceso_carpeta_otro_usuario(auth_client, app):
    """Test acceso a carpeta de otro usuario (debe fallar)"""
    from models import Carpeta, db
    
    with app.app_context():
        # Crear carpeta de otro usuario
        other_folder = Carpeta(nombre="Other", usuario_id=999)
        db.session.add(other_folder)
        db.session.commit()
        folder_id = other_folder.id
    
    response = auth_client.get(f'/?carpeta_id={folder_id}')
    assert response.status_code == 403  # Forbidden
