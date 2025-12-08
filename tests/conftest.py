"""
Fixtures compartidas para tests
"""
import os
import tempfile

import pytest

from app import app as flask_app
from models import Archivo, Carpeta, Usuario, db


@pytest.fixture
def app():
    """Fixture de aplicación Flask para testing"""
    # Configurar app para testing
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    flask_app.config["WTF_CSRF_ENABLED"] = False
    flask_app.config["SECRET_KEY"] = "test-secret-key"

    # Crear directorio temporal para uploads
    temp_dir = tempfile.mkdtemp()
    flask_app.config["UPLOAD_FOLDER"] = temp_dir

    # Crear tablas
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()

    # Limpiar directorio temporal
    import shutil

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
        user = Usuario(nombre="Test User", email="test@example.com")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def carpeta(app, usuario):
    """Fixture de carpeta de prueba"""
    with app.app_context():
        folder = Carpeta(nombre="Test Folder", usuario_id=usuario.id)
        db.session.add(folder)
        db.session.commit()
        return folder


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
        return file


@pytest.fixture
def auth_client(client, usuario):
    """Cliente autenticado"""
    with client:
        client.post("/login", json={"email": usuario.email, "password": "testpass123"})
        yield client
