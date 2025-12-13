"""
Fixtures compartidas para tests
"""

import shutil
import tempfile

import pytest

from app import create_app
from configuracion import TestConfig
from extensiones import db
from modelos import Archivo, Carpeta, Usuario


@pytest.fixture(scope="function")
def app():
    """Fixture de aplicación Flask para testing"""
    # Crear directorio temporal para uploads
    temp_dir = tempfile.mkdtemp()

    # Configuración de prueba con directorio temporal
    class TestCaseConfig(TestConfig):
        UPLOAD_FOLDER = temp_dir

    # Crear app
    test_app = create_app(TestCaseConfig)

    # Contexto de aplicación y BD
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()

    # Limpiar directorio temporal
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """Fixture de cliente de test"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Fixture de CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def usuario(app):
    """Fixture de usuario de prueba"""
    with app.app_context():
        user = Usuario(nombre="Test User", correo="test@example.com", activo=True)
        user.codificar_contrasena("testpass123")
        db.session.add(user)
        db.session.commit()

        # Guardar datos básicos para retornar
        user_data = UserData(user.id, user.correo)
        return user_data


class UserData:
    def __init__(self, id, correo):
        self.id = id
        self.correo = correo


@pytest.fixture
def carpeta(app, usuario):
    """Fixture de carpeta de prueba"""
    with app.app_context():
        folder = Carpeta(nombre="Test Folder", usuario_id=usuario.id)
        db.session.add(folder)
        db.session.commit()
        return FolderData(folder.id)


class FolderData:
    def __init__(self, id):
        self.id = id


@pytest.fixture
def archivo(app, usuario):
    """Fixture de archivo de prueba"""
    with app.app_context():
        file = Archivo(
            nombre_original="test.txt",
            nombre_hash="test_hash.txt",
            tipo="otro",
            tamano="1.0 KB",
            usuario_id=usuario.id,
        )
        db.session.add(file)
        db.session.commit()
        return FileData(file.id)


class FileData:
    def __init__(self, id):
        self.id = id


@pytest.fixture
def auth_client(client, usuario):
    """Cliente autenticado"""
    with client:
        client.post("/inicio_sesion", json={"correo": usuario.correo, "contrasena": "testpass123"})
        yield client
