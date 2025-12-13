from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_login import login_required, login_user, logout_user
from flask_mail import Message

from extensiones import db, mail
from modelos import Usuario
from utils.token import generar_token_confirmacion, verificar_token_confirmacion

auth_bp = Blueprint("auth", __name__)


def enviar_correo_confirmacion(correo, token):
    """Envía un correo de confirmación"""
    enlace = f"http://localhost:5555/confirmar/{token}"

    mensaje = Message("Confirma tu cuenta", sender=current_app.config["MAIL_DEFAULT_SENDER"], recipients=[correo])

    mensaje.body = f"""
    Hola!
    Por favor, confirma tu cuenta haciendo clic en el siguiente enlace: {enlace}

    Gracias por usar Nuvoryx!"""

    mail.send(mensaje)


@auth_bp.route("/enviar_confirmacion/<correo>")
def enviar_confirmacion(correo):
    token = generar_token_confirmacion(correo)
    enviar_correo_confirmacion(correo, token)
    return jsonify({"success": "Correo enviado"}), 200


@auth_bp.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json()
    nombre = datos.get("nombre")
    correo = datos.get("correo")
    contrasena = datos.get("contrasena")

    # Validación
    if not nombre or not correo or not contrasena:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    if len(contrasena) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    # Verificar si el correo ya existe
    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "El email ya está registrado"}), 400

    # Crear nuevo usuario
    nuevo_usuario = Usuario(nombre=nombre, correo=correo)
    nuevo_usuario.codificar_contrasena(contrasena)

    db.session.add(nuevo_usuario)
    db.session.commit()

    token = generar_token_confirmacion(correo)
    enviar_correo_confirmacion(correo, token)

    return (
        jsonify(
            {
                "success": True,
                "usuario": {
                    "id": nuevo_usuario.id,
                    "nombre": nuevo_usuario.nombre,
                    "correo": nuevo_usuario.correo,
                },
            }
        ),
        200,
    )


@auth_bp.route("/confirmar/<token>")
def confirmar(token):
    correo = verificar_token_confirmacion(token)

    if correo:
        usuario = Usuario.query.filter_by(correo=correo).first()

        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        usuario.activo = True
        db.session.commit()

        # Auto-login después del registro
        login_user(usuario)
        return redirect(url_for("main.index"))
    else:
        return redirect(url_for("main.index"))


@auth_bp.route("/inicio_sesion", methods=["POST"])
def inicio_sesion():
    datos = request.get_json()
    correo = datos.get("correo")
    contrasena = datos.get("contrasena")

    if not correo or not contrasena:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    # Buscar usuario
    usuario = Usuario.query.filter_by(correo=correo).first()

    if not usuario or not usuario.verificar_contrasena(contrasena):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if not usuario.activo:
        return jsonify({"error": "El usuario no esta activado"}), 401

    # Login exitoso
    login_user(usuario)
    usuario.ultimo_acceso = db.func.now()
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "usuario": {"id": usuario.id, "nombre": usuario.nombre, "correo": usuario.correo},
        }
    )


@auth_bp.route("/cerrar_sesion", methods=["POST"])
@login_required
def cerrar_sesion():
    logout_user()
    return jsonify({"success": True})


@auth_bp.route("/cambiar_correo", methods=["POST"])
@login_required
def cambiar_correo():
    from flask_login import current_user

    datos = request.get_json()
    nuevo_correo = datos.get("correo")

    if not nuevo_correo:
        return jsonify({"error": "Correo requerido"}), 400

    # Verificar si el correo ya existe
    if Usuario.query.filter_by(correo=nuevo_correo).first():
        return jsonify({"error": "El email ya está registrado"}), 400

    current_user.correo = nuevo_correo
    db.session.commit()
    return jsonify({"success": True, "mensaje": "Correo actualizado"})


@auth_bp.route("/cambiar_password", methods=["POST"])
@login_required
def cambiar_password():
    from flask_login import current_user

    datos = request.get_json()
    contrasena = datos.get("contrasena")

    if not contrasena or len(contrasena) < 6:
        return jsonify({"error": "Contraseña inválida (min 6 caracteres)"}), 400

    current_user.codificar_contrasena(contrasena)
    db.session.commit()
    return jsonify({"success": True, "mensaje": "Contraseña actualizada"})
