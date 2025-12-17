from flask import current_app
from itsdangerous import URLSafeTimedSerializer


def generar_token_confirmacion(correo):
    serializer = URLSafeTimedSerializer(current_app.config["CLAVE_SECRETA"])
    return serializer.dumps(correo, salt=current_app.config["SAL_CONTRASENA_SEGURIDAD"])


def verificar_token_confirmacion(token, expiracion=3600):
    serializer = URLSafeTimedSerializer(current_app.config["CLAVE_SECRETA"])

    try:
        correo = serializer.loads(token, salt=current_app.config["SAL_CONTRASENA_SEGURIDAD"], max_age=expiracion)
        return correo
    except Exception:
        return None
