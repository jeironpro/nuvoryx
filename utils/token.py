from flask import current_app
from itsdangerous import URLSafeTimedSerializer


def generar_token_confirmacion(correo):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(correo, salt=current_app.config["SECURITY_PASSWORD_SALT"])


def verificar_token_confirmacion(token, expiracion=3600):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    correo = serializer.loads(token, salt=current_app.config["SECURITY_PASSWORD_SALT"], max_age=expiracion)

    if correo:
        return correo
    else:
        return None
