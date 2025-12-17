"""
Fixtures compartidas para pruebas
"""

import shutil
import tempfile

import pytest

from app import crear_app
from configuracion import ConfiguracionTest
from extensiones import db
from models import Archivo, Carpeta, Usuario


@pytest.fixture(scope="function")
def app():
    """Fixture de aplicación Flask para pruebas"""
    # Crear directorio temporal para subidas
    directorio_temporal = tempfile.mkdtemp()

    # Configuración de prueba con directorio temporal
    class ConfiguracionPruebas(ConfiguracionTest):
        CARPETA_SUBIDAS = directorio_temporal

    # Crear app
    app_prueba = crear_app(ConfiguracionPruebas)

    # Contexto de aplicación y BD
    with app_prueba.app_context():
        db.create_all()
        yield app_prueba
        db.session.rollback()
        db.session.remove()
        db.drop_all()

    # Limpiar directorio temporal
    shutil.rmtree(directorio_temporal, ignore_errors=True)


@pytest.fixture
def cliente(app):
    """Fixture de cliente de prueba"""
    return app.test_client()


@pytest.fixture
def ejecutor(app):
    """Fixture de ejecutor de CLI"""
    return app.test_cli_runner()


@pytest.fixture
def usuario(app):
    """Fixture de usuario de prueba"""
    with app.app_context():
        user = Usuario(nombre="Usuario Prueba", correo="prueba@example.com", activo=True)
        user.codificar_contrasena("contrasenaprueba123")
        db.session.add(user)
        db.session.commit()

        # Guardar datos básicos para retornar
        datos_usuario = DatosUsuario(user.id, user.correo)
        return datos_usuario


class DatosUsuario:
    def __init__(self, id, correo):
        self.id = id
        self.correo = correo


@pytest.fixture
def carpeta(app, usuario):
    """Fixture de carpeta de prueba"""
    with app.app_context():
        folder = Carpeta(nombre="Carpeta Prueba", usuario_id=usuario.id)
        db.session.add(folder)
        db.session.commit()
        return DatosCarpeta(folder.id)


class DatosCarpeta:
    def __init__(self, id):
        self.id = id


@pytest.fixture
def archivo(app, usuario):
    """Fixture de archivo de prueba"""
    with app.app_context():
        file = Archivo(
            nombre_original="prueba.txt",
            nombre_hash="prueba_hash.txt",
            tipo="otro",
            tamano="1.0 KB",
            usuario_id=usuario.id,
        )
        db.session.add(file)
        db.session.commit()
        return DatosArchivo(file.id)


class DatosArchivo:
    def __init__(self, id):
        self.id = id


@pytest.fixture
def cliente_autenticado(cliente, usuario):
    """Cliente autenticado"""
    with cliente:
        cliente.post("/inicio_sesion", json={"correo": usuario.correo, "contrasena": "contrasenaprueba123"})
        yield cliente
