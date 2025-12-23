from models import Archivo, Carpeta, Usuario, db


def test_crear_usuario(app):
    with app.app_context():
        usuario = Usuario(nombre="Juan Perez", correo="juan@example.com")
        usuario.codificar_contrasena("contrasena123")
        db.session.add(usuario)
        db.session.commit()

        assert usuario.id is not None
        assert usuario.nombre == "Juan Perez"
        assert usuario.correo == "juan@example.com"
        assert usuario.contrasena_hash is not None


def test_verificar_contrasena(app, usuario):
    with app.app_context():
        user = Usuario.query.get(usuario.id)
        assert user.verificar_contrasena("contrasenaprueba123") is True
        assert user.verificar_contrasena("clave_incorrecta") is False


def test_crear_carpeta(app, usuario):
    with app.app_context():
        carpeta_obj = Carpeta(nombre="Mi Carpeta", usuario_id=usuario.id)
        db.session.add(carpeta_obj)
        db.session.commit()

        assert carpeta_obj.id is not None
        assert carpeta_obj.nombre == "Mi Carpeta"
        assert carpeta_obj.usuario_id == usuario.id


def test_crear_archivo(app, usuario):
    with app.app_context():
        archivo_obj = Archivo(
            nombre_original="documento.pdf",
            nombre_hash="hash123.pdf",
            tipo="pdf",
            tamano="2.5 MB",
            usuario_id=usuario.id,
        )
        db.session.add(archivo_obj)
        db.session.commit()

        assert archivo_obj.id is not None
        assert archivo_obj.nombre_original == "documento.pdf"
        assert archivo_obj.tipo == "pdf"
        assert archivo_obj.usuario_id == usuario.id


def test_relacion_usuario_carpetas(app, usuario, carpeta):
    with app.app_context():
        user = Usuario.query.get(usuario.id)
        assert len(user.carpetas) == 1
        assert user.carpetas[0].nombre == "Carpeta Prueba"


def test_relacion_usuario_archivos(app, usuario, archivo):
    with app.app_context():
        user = Usuario.query.get(usuario.id)
        assert len(user.archivos) == 1
        assert user.archivos[0].nombre_original == "prueba.txt"


def test_carpeta_subcarpetas(app, usuario, carpeta):
    with app.app_context():
        padre = Carpeta.query.get(carpeta.id)
        subcarpeta = Carpeta(nombre="Subcarpeta", carpeta_padre_id=padre.id, usuario_id=usuario.id)
        db.session.add(subcarpeta)
        db.session.commit()

        assert len(padre.subcarpetas) == 1
        assert padre.subcarpetas[0].nombre == "Subcarpeta"
