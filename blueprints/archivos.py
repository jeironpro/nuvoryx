import io
import mimetypes
import os
import uuid
import zipfile
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request, send_file, send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from models import Archivo, Carpeta, db
from utils.utilidades import agregar_carpeta_a_zip, borrar_fisicos, detectar_tipo_archivo

archivos_bp = Blueprint("archivos", __name__)


@archivos_bp.route("/crear-carpeta", methods=["POST"])
@login_required
def crear_carpeta():
    """
    Crea una nueva carpeta en la base de datos.
    Permite anidamiento si se proporciona un carpeta_padre_id.
    """
    nombre = request.form.get("nombre")
    carpeta_padre_id = request.form.get("carpeta_padre_id", type=int)

    if not nombre:
        return jsonify({"error": "Nombre requerido"}), 400

    usuario_id = current_user.id if current_user.is_authenticated else None

    nueva_carpeta = Carpeta(nombre=nombre, carpeta_padre_id=carpeta_padre_id, usuario_id=usuario_id)
    db.session.add(nueva_carpeta)

    # Actualizar la fecha de la carpeta padre si existe
    if carpeta_padre_id:
        padre = Carpeta.query.get(carpeta_padre_id)
        if padre:
            padre.fecha_actualizacion = datetime.utcnow()

    db.session.commit()

    return jsonify({"success": True, "id": nueva_carpeta.id, "nombre": nueva_carpeta.nombre})


@archivos_bp.route("/subir", methods=["POST"])
@login_required
def subir_archivo():
    """
    Gestiona la subida de archivos individuales o estructuras completas de carpetas (Drag & Drop).

    Procesa 'rutas_relativas' para recrear la jerarquía de directorios en la base de datos
    antes de guardar el archivo físico con un nombre único (hash).
    """
    if "archivos" not in request.files:
        return jsonify({"error": "No hay archivos en la solicitud"}), 400

    archivos = request.files.getlist("archivos")
    rutas_relativas = request.form.getlist("rutas_relativas")

    carpeta_raiz_id = request.form.get("carpeta_id", type=int)
    usuario_id = current_user.id

    archivos_guardados = []

    # Si no vienen rutas relativas, usamos el nombre del archivo original
    if not rutas_relativas:
        rutas_relativas = [a.filename for a in archivos]

    for archivo, ruta_relativa in zip(archivos, rutas_relativas):
        # Normalización de rutas para evitar problemas entre SOs
        ruta_limpia = ruta_relativa.replace("\\", "/").strip("/")
        partes = ruta_limpia.split("/")

        # Si la ruta tiene niveles, identificamos las carpetas intermedias
        if len(partes) > 1:
            carpetas_a_crear = partes[:-1]
            nombre_archivo = secure_filename(partes[-1])
        else:
            carpetas_a_crear = []
            nombre_archivo = secure_filename(ruta_limpia)

        carpeta_actual_id = carpeta_raiz_id

        # Creación recursiva de la estructura de carpetas en DB
        for nombre_c in carpetas_a_crear:
            carpeta_db = Carpeta.query.filter_by(
                nombre=nombre_c, carpeta_padre_id=carpeta_actual_id, usuario_id=usuario_id
            ).first()

            if not carpeta_db:
                carpeta_db = Carpeta(nombre=nombre_c, carpeta_padre_id=carpeta_actual_id, usuario_id=usuario_id)
                db.session.add(carpeta_db)
                db.session.commit()  # Commit inmediato para obtener ID para la siguiente iteración

            carpeta_actual_id = carpeta_db.id

        # Generación de nombre físico único para evitar colisiones
        extension = os.path.splitext(nombre_archivo)[1].lower()
        nombre_hash = f"{uuid.uuid4().hex}{extension}"
        ruta_fisica = os.path.join(current_app.config["CARPETA_SUBIDAS"], nombre_hash)
        archivo.save(ruta_fisica)

        # Cálculo de tamaño legible para el usuario
        tamano_bytes = os.path.getsize(ruta_fisica)
        if tamano_bytes < 1024:
            tamano_str = f"{tamano_bytes} B"
        elif tamano_bytes < 1024 * 1024:
            tamano_str = f"{tamano_bytes / 1024:.1f} KB"
        else:
            tamano_str = f"{tamano_bytes / (1024 * 1024):.1f} MB"

        tipo_simple = detectar_tipo_archivo(nombre_archivo)

        # Registro del archivo en DB vinculado a la carpeta final de su ruta
        nuevo_archivo = Archivo(
            nombre_original=nombre_archivo,
            nombre_hash=nombre_hash,
            tipo=tipo_simple,
            tamano=tamano_str,
            carpeta_id=carpeta_actual_id,
            usuario_id=usuario_id,
        )
        db.session.add(nuevo_archivo)

        if carpeta_actual_id:
            padre = Carpeta.query.get(carpeta_actual_id)
            if padre:
                padre.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        archivos_guardados.append({"id": nuevo_archivo.id, "nombre": nombre_archivo, "status": "success"})

    return jsonify({"message": "Subida finalizada", "archivos": archivos_guardados})


@archivos_bp.route("/eliminar/<int:archivo_id>", methods=["DELETE"])
def eliminar_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)

    ruta_archivo = os.path.join(current_app.config["CARPETA_SUBIDAS"], archivo.nombre_hash)
    try:
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
    except Exception as e:
        print(f"Error eliminando archivo {ruta_archivo}: {e}")

    parent_id = archivo.carpeta_id
    db.session.delete(archivo)

    if parent_id:
        padre = Carpeta.query.get(parent_id)
        if padre:
            padre.fecha_actualizacion = datetime.utcnow()

    db.session.commit()

    return jsonify({"success": True})


@archivos_bp.route("/eliminar-carpeta/<int:carpeta_id>", methods=["DELETE"])
def eliminar_carpeta_route(carpeta_id):
    carpeta = Carpeta.query.get_or_404(carpeta_id)

    parent_id = carpeta.carpeta_padre_id
    borrar_fisicos(carpeta)
    db.session.delete(carpeta)

    if parent_id:
        padre = Carpeta.query.get(parent_id)
        if padre:
            padre.fecha_actualizacion = datetime.utcnow()

    db.session.commit()

    return jsonify({"success": True})


@archivos_bp.route("/eliminar-multiples", methods=["POST"])
@login_required
def eliminar_multiples():
    """
    Elimina múltiples archivos y carpetas en una sola transacción.
    Espera un JSON con 'ids' (archivos) y 'carpetas_ids' (carpetas).
    """
    data = request.get_json()
    ids = data.get("ids", [])
    carpetas_ids = data.get("carpetas_ids", [])

    if not ids and not carpetas_ids:
        return jsonify({"error": "No se proporcionaron elementos"}), 400

    exitos = 0
    parents_to_update = set()

    # Procesar Archivos
    for archivo_id in ids:
        archivo = Archivo.query.get(archivo_id)
        if archivo and archivo.usuario_id == current_user.id:
            ruta_archivo = os.path.join(current_app.config["CARPETA_SUBIDAS"], archivo.nombre_hash)
            try:
                if os.path.exists(ruta_archivo):
                    os.remove(ruta_archivo)
            except Exception as e:
                current_app.logger.error(f"Error físico: {e}")

            if archivo.carpeta_id:
                parents_to_update.add(archivo.carpeta_id)
            db.session.delete(archivo)
            exitos += 1

    # Procesar Carpetas
    for carpeta_id in carpetas_ids:
        carpeta = Carpeta.query.get(carpeta_id)
        if carpeta and carpeta.usuario_id == current_user.id:
            if carpeta.carpeta_padre_id:
                parents_to_update.add(carpeta.carpeta_padre_id)
            borrar_fisicos(carpeta)
            db.session.delete(carpeta)
            exitos += 1

    # Actualizar fechas
    for p_id in parents_to_update:
        if p_id:
            padre = Carpeta.query.get(int(p_id))
            if padre:
                padre.fecha_actualizacion = datetime.utcnow()

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error en commit masivo: {e}")
        return jsonify({"success": False, "error": "No se pudo completar la transacción de borrado."}), 500

    return jsonify({"success": True, "count": exitos})


@archivos_bp.route("/descargar-zip", methods=["POST"])
@login_required
def descargar_zip():
    data = request.get_json()
    ids = data.get("ids", [])
    carpetas_ids = data.get("carpetas_ids", [])

    if not ids and not carpetas_ids:
        return jsonify({"error": "Sin elementos para descargar"}), 400

    memoria_archivo = io.BytesIO()
    with zipfile.ZipFile(memoria_archivo, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Procesar archivos individuales
        for archivo_id in ids:
            archivo = db.session.get(Archivo, archivo_id)
            if archivo and archivo.usuario_id == current_user.id:
                ruta = os.path.join(current_app.config["CARPETA_SUBIDAS"], archivo.nombre_hash)
                if os.path.exists(ruta):
                    zipf.write(ruta, arcname=archivo.nombre_original)

        # Procesar carpetas completas
        for carpeta_id in carpetas_ids:
            carpeta = db.session.get(Carpeta, carpeta_id)
            if carpeta and carpeta.usuario_id == current_user.id:
                agregar_carpeta_a_zip(zipf, carpeta)

    memoria_archivo.seek(0)
    return send_file(
        memoria_archivo,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"nuvoryx_pack_{datetime.now().strftime('%Y%m%d%H%M')}.zip",
    )


@archivos_bp.route("/descargar-carpeta/<int:carpeta_id>", methods=["GET"])
def descargar_carpeta(carpeta_id):
    carpeta = Carpeta.query.get_or_404(carpeta_id)

    memoria_archivo = io.BytesIO()

    try:
        with zipfile.ZipFile(memoria_archivo, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
            agregar_carpeta_a_zip(archivo_zip, carpeta)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    memoria_archivo.seek(0)

    zip_filename = f"{carpeta.nombre}.zip"

    return send_file(memoria_archivo, mimetype="application/zip", as_attachment=True, download_name=zip_filename)


@archivos_bp.route("/descargar/<int:archivo_id>", methods=["GET"])
def descargar_archivo(archivo_id):
    archivo = db.session.get(Archivo, archivo_id)
    if not archivo:
        return jsonify({"error": "Archivo no encontrado"}), 404

    inline = request.args.get("inline", "false").lower() == "true"
    mimetype, _ = mimetypes.guess_type(archivo.nombre_original)

    # Forzar texto para archivos de configuración que mimetypes suele ignorar
    if not mimetype:
        n_bajo = archivo.nombre_original.lower()
        if archivo.nombre_original.startswith(".") or n_bajo in [
            "dockerfile",
            "procfile",
            "readme",
            "license",
            "makefile",
        ]:
            mimetype = "text/plain"
        else:
            mimetype = "application/octet-stream"

    return send_from_directory(
        current_app.config["CARPETA_SUBIDAS"],
        archivo.nombre_hash,
        as_attachment=not inline,
        download_name=archivo.nombre_original,
        mimetype=mimetype,
    )
