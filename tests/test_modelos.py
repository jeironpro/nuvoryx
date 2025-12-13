"""
Tests para modelos de base de datos
"""

from modelos import Archivo, Carpeta, Usuario, db


def test_crear_usuario(app):
    """Test crear usuario"""
    with app.app_context():
        user = Usuario(nombre="John Doe", correo="john@example.com")
        user.codificar_contrasena("password123")
        db.session.add(user)
        db.session.commit()

        assert user.id is not None
        assert user.nombre == "John Doe"
        assert user.correo == "john@example.com"
        assert user.contrasena_hash is not None


def test_verificar_contrasena(app, usuario):
    """Test verificación de contraseña"""
    with app.app_context():
        user = Usuario.query.get(usuario.id)
        assert user.verificar_contrasena("testpass123") is True
        assert user.verificar_contrasena("wrongpass") is False


def test_crear_carpeta(app, usuario):
    """Test crear carpeta"""
    with app.app_context():
        folder = Carpeta(nombre="My Folder", usuario_id=usuario.id)
        db.session.add(folder)
        db.session.commit()

        assert folder.id is not None
        assert folder.nombre == "My Folder"
        assert folder.usuario_id == usuario.id


def test_crear_archivo(app, usuario):
    """Test crear archivo"""
    with app.app_context():
        file = Archivo(
            nombre_original="document.pdf",
            nombre_hash="hash123.pdf",
            tipo="pdf",
            tamano="2.5 MB",
            usuario_id=usuario.id,
        )
        db.session.add(file)
        db.session.commit()

        assert file.id is not None
        assert file.nombre_original == "document.pdf"
        assert file.tipo == "pdf"
        assert file.usuario_id == usuario.id


def test_relacion_usuario_carpetas(app, usuario, carpeta):
    """Test relación usuario-carpetas"""
    with app.app_context():
        user = Usuario.query.get(usuario.id)
        assert len(user.carpetas) == 1
        assert user.carpetas[0].nombre == "Test Folder"


def test_relacion_usuario_archivos(app, usuario, archivo):
    """Test relación usuario-archivos"""
    with app.app_context():
        user = Usuario.query.get(usuario.id)
        assert len(user.archivos) == 1
        assert user.archivos[0].nombre_original == "test.txt"


def test_carpeta_subcarpetas(app, usuario, carpeta):
    """Test subcarpetas"""
    with app.app_context():
        parent = Carpeta.query.get(carpeta.id)
        subfolder = Carpeta(nombre="Subfolder", carpeta_padre_id=parent.id, usuario_id=usuario.id)
        db.session.add(subfolder)
        db.session.commit()

        assert len(parent.subcarpetas) == 1
        assert parent.subcarpetas[0].nombre == "Subfolder"
