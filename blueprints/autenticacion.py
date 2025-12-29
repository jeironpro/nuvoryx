from flask import Blueprint, current_app, jsonify, redirect, request, url_for
from flask_login import login_required, login_user, logout_user
from flask_mail import Message

from extensiones import db, mail
from models import Usuario
from utils.token import generar_token_confirmacion, verificar_token_confirmacion

autenticacion_bp = Blueprint("autenticacion", __name__)


def enviar_correo_confirmacion(correo, token):
    """Envía un enlace de activación de cuenta al correo electrónico del nuevo usuario."""
    enlace = f"http://localhost:5000/confirmar/{token}"
    mensaje = Message(
        "Confirma tu cuenta", sender=current_app.config["REMITENTE_POR_DEFECTO_CORREO"], recipients=[correo]
    )
    mensaje.body = f"Hola!\nPor favor, confirma tu cuenta haciendo clic en el siguiente enlace: {enlace}\n\nGracias por usar Nuvoryx!"
    mail.send(mensaje)


def enviar_correo_restablecimiento(correo, token):
    """Envía un enlace para cambiar la contraseña en caso de olvido."""
    enlace = f"http://localhost:5000/restablecer/{token}"
    mensaje = Message(
        "Restablecer tu contraseña",
        sender=current_app.config["REMITENTE_POR_DEFECTO_CORREO"],
        recipients=[correo],
    )
    mensaje.body = (
        f"Hola!\nHas solicitado restablecer tu contraseña. Haz clic en el enlace: {enlace}\n\nGracias por usar Nuvoryx!"
    )
    mail.send(mensaje)


@autenticacion_bp.route("/registro", methods=["POST"])
def registro():
    """Registra a un nuevo usuario y le envía un correo de confirmación."""
    datos = request.get_json()
    nombre = datos.get("nombre")
    correo = datos.get("correo")
    contrasena = datos.get("contrasena")

    if not nombre or not correo or not contrasena:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    if len(contrasena) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "El email ya está registrado"}), 400

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
    """Verifica el token de correo y activa la cuenta del usuario."""
    correo = verificar_token_confirmacion(token)

    if correo:
        usuario = Usuario.query.filter_by(correo=correo).first()
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        usuario.activo = True
        db.session.commit()
        login_user(usuario)
        return redirect(url_for("principal.indice"))

    return redirect(url_for("principal.indice"))


@autenticacion_bp.route("/inicio_sesion", methods=["POST"])
def inicio_sesion():
    """Valida credenciales e inicia la sesión del usuario."""
    datos = request.get_json()
    correo = datos.get("correo")
    contrasena = datos.get("contrasena")

    if not correo or not contrasena:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    usuario = Usuario.query.filter_by(correo=correo).first()

    if not usuario or not usuario.verificar_contrasena(contrasena):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if not usuario.activo:
        return jsonify({"error": "El usuario no está activado"}), 401

    login_user(usuario)
    usuario.ultimo_acceso = db.func.now()
    db.session.commit()

    return jsonify({"success": True, "usuario": {"id": usuario.id, "nombre": usuario.nombre, "correo": usuario.correo}})


@autenticacion_bp.route("/cerrar_sesion", methods=["POST"])
@login_required
def cerrar_sesion():
    logout_user()
    return jsonify({"success": True})


@autenticacion_bp.route("/cambiar_correo", methods=["POST"])
@login_required
def cambiar_correo():
    """
    Permite al usuario cambiar su correo electrónico.
    Verifica la contraseña actual y envía una notificación al nuevo correo.
    """
    from flask_login import current_user

    datos = request.get_json()
    nuevo_correo = datos.get("correo")

    if not nuevo_correo:
        return jsonify({"error": "Correo requerido"}), 400

    if Usuario.query.filter_by(correo=nuevo_correo).first():
        return jsonify({"error": "El email ya está registrado"}), 400

    # Guardar referencia al correo anterior
    correo_anterior = current_user.correo
    current_user.correo = nuevo_correo
    db.session.commit()

    # Enviar avisos de seguridad
    enviar_aviso_cambio_correo(correo_anterior, nuevo_correo)

    return jsonify({"success": True, "mensaje": "Correo actualizado. Se han enviado avisos de seguridad."})


def enviar_aviso_cambio_correo(correo_anterior, nuevo_correo):
    # Aviso al correo antiguo
    mensaje_antiguo = Message(
        "Aviso de cambio de correo - Nuvoryx",
        sender=current_app.config["REMITENTE_POR_DEFECTO_CORREO"],
        recipients=[correo_anterior],
    )
    mensaje_antiguo.body = f"""
    Hola!
    Te informamos que la dirección de correo electrónico asociada a tu cuenta de Nuvoryx ha sido cambiada a: {nuevo_correo}.

    Si no has realizado este cambio, por favor ponte en contacto con el soporte de inmediato.

    Gracias por usar Nuvoryx!"""
    mail.send(mensaje_antiguo)

    # Aviso al correo nuevo
    mensaje_nuevo = Message(
        "Aviso de cambio de correo - Nuvoryx",
        sender=current_app.config["REMITENTE_POR_DEFECTO_CORREO"],
        recipients=[nuevo_correo],
    )
    mensaje_nuevo.body = f"""
    Hola!
    Te informamos que has cambiado correctamente tu dirección de correo electrónico a esta cuenta ({nuevo_correo}).

    Si no has realizado este cambio, por favor ponte en contacto con el soporte de inmediato.

    Gracias por usar Nuvoryx!"""
    mail.send(mensaje_nuevo)


@autenticacion_bp.route("/cambiar_password", methods=["POST"])
@login_required
def cambiar_password():
    """
    Actualiza la contraseña del usuario tras validar la actual.
    Envía un aviso de seguridad por correo electrónico al finalizar con éxito.
    """
    from flask_login import current_user

    datos = request.get_json()
    contrasena = datos.get("contrasena")

    if not contrasena or len(contrasena) < 6:
        return jsonify({"error": "Contraseña inválida (min 6 caracteres)"}), 400

    current_user.codificar_contrasena(contrasena)
    db.session.commit()

    # Enviar aviso
    enviar_aviso_cambio_contrasena(current_user.correo)

    return jsonify({"success": True, "mensaje": "Contraseña actualizada"})


def enviar_aviso_cambio_contrasena(correo):
    mensaje = Message(
        "Aviso de cambio de contraseña - Nuvoryx",
        sender=current_app.config["REMITENTE_POR_DEFECTO_CORREO"],
        recipients=[correo],
    )
    mensaje.body = """
    Hola!
    Te informamos que la contraseña de tu cuenta de Nuvoryx ha sido actualizada recientemente.

    Si no has realizado este cambio, por favor restablece tu contraseña de inmediato desde la página de inicio.

    Gracias por usar Nuvoryx!"""
    mail.send(mensaje)


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

    return (
        jsonify({"success": True, "mensaje": "Si el correo está registrado, recibirás un enlace de recuperación."}),
        200,
    )


@autenticacion_bp.route("/restablecer/<token>")
def restablecer_verificar(token):
    correo = verificar_token_confirmacion(token)

    if correo:
        return redirect(url_for("principal.indice", reset_token=token))
    else:
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

    if not usuario.activo:
        usuario.activo = True

    db.session.commit()

    return jsonify({"success": True, "mensaje": "Tu contraseña ha sido restablecida con éxito."})
