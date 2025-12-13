from flask import Flask, render_template

from configuracion import Config
from extensiones import db, login_manager, mail
from modelos import Usuario


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    # Configure Login Manager
    login_manager.login_view = "main.index"

    @login_manager.user_loader
    def cargar_usuario(usuario_id):
        return Usuario.query.get(int(usuario_id))

    # Register blueprints
    # Register blueprints
    from blueprints.archivos import files_bp
    from blueprints.autenticacion import auth_bp
    from blueprints.principal import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    # Create tables
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5555)
