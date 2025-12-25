from flask import Flask, render_template

from configuracion import Configuracion
from extensiones import db, gestor_login, mail
from models import Usuario


def crear_app(clase_config=Configuracion):
    """
    Fábrica de aplicaciones de Flask.
    Inicializa configuraciones, bases de datos y registra los blueprints del sistema.
    """
    app = Flask(__name__)
    app.config.from_object(clase_config)

    # Configuración de seguridad y base de datos
    app.config["SECRET_KEY"] = app.config.get("CLAVE_SECRETA")
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config.get("URI_BASE_DATOS_SQLALCHEMY")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = app.config.get("SEGUIMIENTO_MODIFICACIONES_SQLALCHEMY")
    app.config["MAX_CONTENT_LENGTH"] = app.config.get("TAMANO_MAXIMO_CONTENIDO")

    # Configuración del servidor de correo
    app.config["MAIL_SERVER"] = app.config.get("SERVIDOR_CORREO")
    app.config["MAIL_PORT"] = app.config.get("PUERTO_CORREO")
    app.config["MAIL_USE_TLS"] = app.config.get("USAR_TLS_CORREO")
    app.config["MAIL_USERNAME"] = app.config.get("USUARIO_CORREO")
    app.config["MAIL_PASSWORD"] = app.config.get("CONTRASENA_CORREO")
    app.config["MAIL_DEFAULT_SENDER"] = app.config.get("REMITENTE_POR_DEFECTO_CORREO")
    app.config["WTF_CSRF_ENABLED"] = app.config.get("HABILITAR_CSRF_WTF", True)

    # Inicialización de extensiones
    db.init_app(app)
    mail.init_app(app)
    gestor_login.init_app(app)

    with app.app_context():
        db.create_all()

    # Configuración de la vista de login por defecto
    gestor_login.login_view = "principal.indice"

    @gestor_login.user_loader
    def cargar_usuario(usuario_id):
        """Carga el usuario desde la sesión para Flask-Login."""
        return Usuario.query.get(int(usuario_id))

    # Importación de controladores (blueprints)
    from blueprints.archivos import archivos_bp
    from blueprints.autenticacion import autenticacion_bp
    from blueprints.notificaciones import notificaciones_bp
    from blueprints.principal import principal_bp

    # Registro de rutas modulares
    app.register_blueprint(principal_bp)
    app.register_blueprint(autenticacion_bp)
    app.register_blueprint(archivos_bp)
    app.register_blueprint(notificaciones_bp)

    # Manejo de errores globales
    @app.errorhandler(404)
    def pagina_no_encontrada(e):
        """Redirección personalizada para errores 404."""
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def prohibido(e):
        """Redirección personalizada para errores 403 (Acceso Denegado)."""
        return render_template("403.html"), 403

    return app


if __name__ == "__main__":
    # Inicio del servidor en modo desarrollo
    app = crear_app()
    app.run(debug=True, port=5000)
