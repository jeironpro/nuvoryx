from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required

from extensiones import db
from models import Notificacion

notificaciones_bp = Blueprint("notificaciones", __name__)


@notificaciones_bp.route("/notificaciones", methods=["GET"])
@login_required
def obtener_notificaciones():
    notificaciones = (
        Notificacion.query.filter_by(usuario_id=current_user.id).order_by(Notificacion.fecha.desc()).limit(50).all()
    )
    return jsonify(
        [
            {"id": n.id, "mensaje": n.mensaje, "fecha": n.fecha.strftime("%H:%M:%S"), "leida": n.leida, "tipo": n.tipo}
            for n in notificaciones
        ]
    )


@notificaciones_bp.route("/notificaciones", methods=["POST"])
@login_required
def crear_notificacion():
    data = request.get_json()
    if not data or "mensaje" not in data:
        return jsonify({"success": False, "error": "Falta el mensaje"}), 400

    nueva = Notificacion(usuario_id=current_user.id, mensaje=data["mensaje"], tipo=data.get("tipo", "info"))
    db.session.add(nueva)
    db.session.commit()
    return jsonify({"success": True, "id": nueva.id})


@notificaciones_bp.route("/notificaciones/limpiar", methods=["DELETE"])
@login_required
def limpiar_notificaciones():
    Notificacion.query.filter_by(usuario_id=current_user.id).delete()
    db.session.commit()
    return jsonify({"success": True})


@notificaciones_bp.route("/notificaciones/marcar-leidas", methods=["POST"])
@login_required
def marcar_leidas():
    Notificacion.query.filter_by(usuario_id=current_user.id, leida=False).update({"leida": True})
    db.session.commit()
    return jsonify({"success": True})
