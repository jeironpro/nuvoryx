from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_login import login_required, login_user, logout_user
from flask_mail import Message

from extensiones import db, mail
from models import Usuario
from utils.token import generar_token_confirmacion, verificar_token_confirmacion

autenticacion_bp = Blueprint("autenticacion", __name__)


def enviar_correo_confirmacion(correo, token):
    """Envía un correo de confirmación"""
    enlace = f"http://localhost:5555/confirmar/{token}"

    mensaje = Message(
        "Confirma tu cuenta", sender=current_app.config["REMITENTE_POR_DEFECTO_CORREO"], recipients=[correo]
    )

    mensaje.body = f"""
    Hola!
    Por favor, confirma tu cuenta haciendo clic en el siguiente enlace: {enlace}

    Gracias por usar Nuvoryx!"""

    mail.send(mensaje)


def enviar_correo_restablecimiento(correo, token):
    """Envía un correo para restablecer la contraseña"""
    enlace = f"http://localhost:5555/restablecer/{token}"

    mensaje = Message(
        "Restablecer tu contraseña",
        sender=current_app.config["REMITENTE_POR_DEFECTO_CORREO"],
        recipients=[correo],
    )

    mensaje.body = f"""
    Hola!
    Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace para continuar: {enlace}

    Si no has solicitado esto, puedes ignorar este correo.

    Gracias por usar Nuvoryx!"""

    mail.send(mensaje)


@autenticacion_bp.route("/enviar_confirmacion/<correo>")
def enviar_confirmacion(correo):
    token = generar_token_confirmacion(correo)
    enviar_correo_confirmacion(correo, token)
    return jsonify({"success": "Correo enviado"}), 200


@autenticacion_bp.route("/registro", methods=["POST"])
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


@autenticacion_bp.route("/confirmar/<token>")
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
        return redirect(url_for("principal.indice"))
    else:
        return redirect(url_for("principal.indice"))


@autenticacion_bp.route("/inicio_sesion", methods=["POST"])
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


@autenticacion_bp.route("/cerrar_sesion", methods=["POST"])
@login_required
def cerrar_sesion():
    logout_user()
    return jsonify({"success": True})


@autenticacion_bp.route("/cambiar_correo", methods=["POST"])
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


@autenticacion_bp.route("/cambiar_password", methods=["POST"])
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


@autenticacion_bp.route("/olvido_password", methods=["POST"])
def olvido_password():
    datos = request.get_json()
    correo = datos.get("correo")

    if not correo:
        return jsonify({"error": "Correo electrónico requerido"}), 400

    usuario = Usuario.query.filter_by(correo=correo).first()

    if usuario:
        token = generar_token_confirmacion(correo)
        enviar_correo_restablecimiento(correo, token)

    # Respondemos con éxito siempre por seguridad (no revelar si el correo existe)
    return (
        jsonify({"success": True, "mensaje": "Si el correo está registrado, recibirás un enlace de recuperación."}),
        200,
    )


@autenticacion_bp.route("/restablecer/<token>")
def restablecer_verificar(token):
    correo = verificar_token_confirmacion(token)

    if correo:
        # Redirigir a la home con el token para que el JS abra el modal
        return redirect(url_for("principal.indice", reset_token=token))
    else:
        # Token inválido o expirado
        return redirect(url_for("principal.indice", error="token_invalido"))


@autenticacion_bp.route("/restablecer_password", methods=["POST"])
def restablecer_password():
    datos = request.get_json()
    token = datos.get("token")
    contrasena = datos.get("contrasena")

    if not token or not contrasena:
        return jsonify({"error": "Token y contraseña son requeridos"}), 400

    correo = verificar_token_confirmacion(token)

    if not correo:
        return jsonify({"error": "El enlace ha expirado o es inválido"}), 400

    usuario = Usuario.query.filter_by(correo=correo).first()

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if len(contrasena) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    usuario.codificar_contrasena(contrasena)
    # También activar al usuario si no lo estaba (opcional, pero común)
    if not usuario.activo:
        usuario.activo = True

    db.session.commit()

    return jsonify({"success": True, "mensaje": "Tu contraseña ha sido restablecida con éxito."})
