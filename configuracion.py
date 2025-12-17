import os

from dotenv import load_dotenv

load_dotenv()


class Configuracion:
    URI_BASE_DATOS_SQLALCHEMY = os.getenv("DATABASE_URL")
    SEGUIMIENTO_MODIFICACIONES_SQLALCHEMY = os.getenv("TRACK_MODIFICATIONS")
    CARPETA_SUBIDAS = os.getenv("UPLOAD_FOLDER")
    TAMANO_MAXIMO_CONTENIDO = int(os.getenv("MAX_CONTENT_LENGTH", 500 * 1024 * 1024))
    CLAVE_SECRETA = os.getenv("SECRET_KEY")
    SAL_CONTRASENA_SEGURIDAD = os.getenv("SECURITY_PASSWORD_SALT")

    SERVIDOR_CORREO = os.getenv("MAIL_SERVER")
    PUERTO_CORREO = int(os.getenv("MAIL_PORT", 587))
    USAR_TLS_CORREO = os.getenv("MAIL_USE_TLS", "True") == "True"
    USUARIO_CORREO = os.getenv("MAIL_USERNAME")
    CONTRASENA_CORREO = os.getenv("MAIL_PASSWORD")
    REMITENTE_POR_DEFECTO_CORREO = os.getenv("MAIL_USERNAME")


class ConfiguracionTest(Configuracion):
    TESTING = True
    URI_BASE_DATOS_SQLALCHEMY = "sqlite:///:memory:"
    SEGUIMIENTO_MODIFICACIONES_SQLALCHEMY = False
    HABILITAR_CSRF_WTF = False
    CLAVE_SECRETA = "clave-secreta-solo-para-tests"
    SAL_CONTRASENA_SEGURIDAD = "sal-seguridad-test"
    TAMANO_MAXIMO_CONTENIDO = 500 * 1024 * 1024
