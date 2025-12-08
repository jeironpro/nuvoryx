"""
Fixtures compartidas para tests
"""

import tempfile

import pytest
from flask import Flask
from flask_login import LoginManager

from models import Archivo, Carpeta, Usuario, db


@pytest.fixture(scope="function")
def app():
    """Fixture de aplicación Flask para testing - crea una app completamente nueva"""
    # Obtener el directorio raíz del proyecto
    import pathlib

    project_root = pathlib.Path(__file__).parent.parent

    # Crear una nueva instancia de Flask para tests con rutas correctas
    test_app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )

    # Configurar SOLO para testing (NO usa la config de producción)
    test_app.config["TESTING"] = True
    test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    test_app.config["WTF_CSRF_ENABLED"] = False
    test_app.config["SECRET_KEY"] = "test-secret-key-only-for-testing"
    test_app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

    # Crear directorio temporal para uploads
    temp_dir = tempfile.mkdtemp()
    test_app.config["UPLOAD_FOLDER"] = temp_dir

    # Inicializar extensiones
    db.init_app(test_app)

    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(test_app)
    login_manager.login_view = "root"

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Importar y registrar rutas DENTRO del contexto de la app de test
    with test_app.app_context():
        # Importar las rutas aquí para que usen esta app
        from app import (
            crear_carpeta,
            descargar_archivo,
            descargar_carpeta,
            descargar_zip,
            eliminar_archivo,
            eliminar_carpeta_route,
            eliminar_multiples,
            login,
            logout,
            register,
            root,
            subir_archivo,
        )

        # Registrar rutas
        test_app.add_url_rule("/", "root", root, methods=["GET"])
        test_app.add_url_rule("/crear-carpeta", "crear_carpeta", crear_carpeta, methods=["POST"])
        test_app.add_url_rule("/subir", "subir_archivo", subir_archivo, methods=["POST"])
        test_app.add_url_rule(
            "/eliminar/<int:archivo_id>", "eliminar_archivo", eliminar_archivo, methods=["DELETE"]
        )
        test_app.add_url_rule(
            "/eliminar-carpeta/<int:carpeta_id>",
            "eliminar_carpeta",
            eliminar_carpeta_route,
            methods=["DELETE"],
        )
        test_app.add_url_rule(
            "/eliminar-multiples", "eliminar_multiples", eliminar_multiples, methods=["POST"]
        )
        test_app.add_url_rule("/descargar-zip", "descargar_zip", descargar_zip, methods=["POST"])
        test_app.add_url_rule(
            "/descargar-carpeta/<int:carpeta_id>",
            "descargar_carpeta",
            descargar_carpeta,
            methods=["GET"],
        )
        test_app.add_url_rule(
            "/descargar/<int:archivo_id>", "descargar_archivo", descargar_archivo, methods=["GET"]
        )
        test_app.add_url_rule("/register", "register", register, methods=["POST"])
        test_app.add_url_rule("/login", "login", login, methods=["POST"])
        test_app.add_url_rule("/logout", "logout", logout, methods=["POST"])

        # Crear tablas en SQLite en memoria
        db.create_all()

        yield test_app

        # Limpiar
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
    """Fixture de usuario de prueba - retorna el objeto dentro del contexto"""
    with app.app_context():
        user = Usuario(nombre="Test User", email="test@example.com")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        # Refrescar para asegurar que los datos están cargados
        db.session.refresh(user)
        user_id = user.id
        user_email = user.email

    # Crear un objeto simple con los datos necesarios
    class UserData:
        def __init__(self, id, email):
            self.id = id
            self.email = email

    return UserData(user_id, user_email)


@pytest.fixture
def carpeta(app, usuario):
    """Fixture de carpeta de prueba"""
    with app.app_context():
        folder = Carpeta(nombre="Test Folder", usuario_id=usuario.id)
        db.session.add(folder)
        db.session.commit()
        folder_id = folder.id

    class FolderData:
        def __init__(self, id):
            self.id = id

    return FolderData(folder_id)


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
        file_id = file.id

    class FileData:
        def __init__(self, id):
            self.id = id

    return FileData(file_id)


@pytest.fixture
def auth_client(client, usuario):
    """Cliente autenticado"""
    with client:
        client.post("/login", json={"email": usuario.email, "password": "testpass123"})
        yield client
