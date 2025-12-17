import io
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
    nombre = request.form.get("nombre")
    carpeta_padre_id = request.form.get("carpeta_padre_id", type=int)

    if not nombre:
        return jsonify({"error": "Nombre requerido"}), 400

    # Asignar usuario_id si está autenticado
    usuario_id = current_user.id if current_user.is_authenticated else None

    nueva_carpeta = Carpeta(nombre=nombre, carpeta_padre_id=carpeta_padre_id, usuario_id=usuario_id)
    db.session.add(nueva_carpeta)

    # Actualizar fecha de la carpeta padre
    if carpeta_padre_id:
        padre = Carpeta.query.get(carpeta_padre_id)
        if padre:
            padre.fecha_actualizacion = datetime.utcnow()

    db.session.commit()

    return jsonify({"success": True, "id": nueva_carpeta.id, "nombre": nueva_carpeta.nombre})


@archivos_bp.route("/subir", methods=["POST"])
@login_required
def subir_archivo():
    if "archivos" not in request.files:
        return jsonify({"error": "No file part"}), 400

    archivos = request.files.getlist("archivos")
    rutas_relativas = request.form.getlist("rutas_relativas")

    carpeta_raiz_id = request.form.get("carpeta_id", type=int)
    usuario_id = current_user.id

    archivos_guardados = []

    for archivo, ruta_relativa in zip(archivos, rutas_relativas):
        # ---------------------------------------
        # 1. Separar carpetas y nombre de archivo
        # ---------------------------------------
        partes = ruta_relativa.split("/")
        carpetas = partes[:-1]  # todas menos el archivo final
        nombre_archivo = secure_filename(partes[-1])

        # ---------------------------------------
        # 2. Crear recursivamente estructura
        # ---------------------------------------
        carpeta_actual_id = carpeta_raiz_id

        for c in carpetas:
            carpeta_db = Carpeta.query.filter_by(
                nombre=c, carpeta_padre_id=carpeta_actual_id, usuario_id=usuario_id
            ).first()

            if not carpeta_db:
                carpeta_db = Carpeta(nombre=c, carpeta_padre_id=carpeta_actual_id, usuario_id=usuario_id)
                db.session.add(carpeta_db)
                db.session.commit()

            carpeta_actual_id = carpeta_db.id

        # ---------------------------------------
        # 3. Guardar archivo en disco
        # ---------------------------------------
        extension_archivo = os.path.splitext(nombre_archivo)[1].lower()
        nombre_hash = f"{uuid.uuid4().hex}{extension_archivo}"
        ruta_archivo = os.path.join(current_app.config["CARPETA_SUBIDAS"], nombre_hash)
        archivo.save(ruta_archivo)

        # Tamaño
        tamano_bytes = os.path.getsize(ruta_archivo)
        if tamano_bytes < 1024:
            tamano_str = f"{tamano_bytes} B"
        elif tamano_bytes < 1024 * 1024:
            tamano_str = f"{tamano_bytes / 1024:.1f} KB"
        else:
            tamano_str = f"{tamano_bytes / (1024 * 1024):.1f} MB"

        # Tipo
        tipo_simple = detectar_tipo_archivo(nombre_archivo)

        # ---------------------------------------
        # 4. Guardar en base de datos
        # ---------------------------------------
        nuevo_archivo = Archivo(
            nombre_original=nombre_archivo,
            nombre_hash=nombre_hash,
            tipo=tipo_simple,
            tamano=tamano_str,
            carpeta_id=carpeta_actual_id,
            usuario_id=usuario_id,
        )
        db.session.add(nuevo_archivo)

        # Actualizar fecha de la carpeta contenedora
        if carpeta_actual_id:
            padre = Carpeta.query.get(carpeta_actual_id)
            if padre:
                padre.fecha_actualizacion = datetime.utcnow()

        db.session.commit()

        archivos_guardados.append(
            {
                "id": nuevo_archivo.id,
                "nombre": nombre_archivo,
                "status": "success",
            }
        )

    return jsonify({"message": "Archivos subidos", "archivos": archivos_guardados})


@archivos_bp.route("/eliminar/<int:archivo_id>", methods=["DELETE"])
def eliminar_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)

    # Eliminar del disco
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
def eliminar_multiples():
    data = request.get_json()
    ids = data.get("ids", [])

    if not ids:
        return jsonify({"error": "No IDs proporcionados"}), 400

    exitos = 0
    errores = 0

    parents_to_update = set()

    for archivo_id in ids:
        archivo = Archivo.query.get(archivo_id)
        if archivo:
            if archivo.carpeta_id:
                parents_to_update.add(archivo.carpeta_id)
            # Eliminar del disco
            ruta_archivo = os.path.join(current_app.config["CARPETA_SUBIDAS"], archivo.nombre_hash)
            try:
                if os.path.exists(ruta_archivo):
                    os.remove(ruta_archivo)
            except Exception as e:
                print(f"Error eliminando archivo {ruta_archivo}: {e}")
                errores += 1
                continue

            # Eliminar de BD
            db.session.delete(archivo)
            exitos += 1
    # Eliminar Carpetas
    carpetas_ids = data.get("carpetas_ids", [])
    for carpeta_id in carpetas_ids:
        carpeta = Carpeta.query.get(carpeta_id)
        if carpeta:
            if carpeta.carpeta_padre_id:
                parents_to_update.add(carpeta.carpeta_padre_id)
            # Aquí idealmente deberíamos eliminar recursivamente
            # los archivos físicos dentro. Por simplicidad delegamos
            # en cascade delete de la BD para los registros.

            borrar_fisicos(carpeta)
            db.session.delete(carpeta)
            exitos += 1

    # Actualizar fechas de las carpetas padres afectadas
    for p_id in parents_to_update:
        padre = Carpeta.query.get(p_id)
        if padre:
            padre.fecha_actualizacion = datetime.utcnow()

    db.session.commit()
    return jsonify({"success": True, "deleted": exitos, "errors": errores})


@archivos_bp.route("/descargar-zip", methods=["POST"])
def descargar_zip():
    # Obtener IDs del formulario (si se usa form submit) o JSON
    if request.is_json:
        datos = request.get_json()
        ids = datos.get("ids", [])
    else:
        # Si viene de un formulario tradicional (hidden inputs)
        ids = request.form.getlist("ids[]")

    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    # Crear buffer en memoria para el ZIP
    memoria_archivo = io.BytesIO()

    try:
        with zipfile.ZipFile(memoria_archivo, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
            for archivo_id in ids:
                archivo = Archivo.query.get(archivo_id)

                if archivo:
                    ruta_archivo = os.path.join(current_app.config["CARPETA_SUBIDAS"], archivo.nombre_hash)

                    if os.path.exists(ruta_archivo):
                        # Añadir al zip con el nombre original
                        # Manejo de duplicados de nombre en el zip podría requerir lógica extra,
                        # pero por simplicidad usaremos nombre original
                        archivo_zip.write(ruta_archivo, arcname=archivo.nombre_original)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    memoria_archivo.seek(0)

    return send_file(
        memoria_archivo,
        mimetype="application/zip",
        as_attachment=True,
        download_name="archivos_descargados.zip",
    )


@archivos_bp.route("/descargar-carpeta/<int:carpeta_id>", methods=["GET"])
def descargar_carpeta(carpeta_id):
    carpeta = Carpeta.query.get_or_404(carpeta_id)

    # Crear buffer en memoria para el ZIP
    memoria_archivo = io.BytesIO()

    try:
        with zipfile.ZipFile(memoria_archivo, "w", zipfile.ZIP_DEFLATED) as archivo_zip:
            agregar_carpeta_a_zip(archivo_zip, carpeta)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    memoria_archivo.seek(0)

    # Nombre del archivo ZIP
    zip_filename = f"{carpeta.nombre}.zip"

    return send_file(memoria_archivo, mimetype="application/zip", as_attachment=True, download_name=zip_filename)


@archivos_bp.route("/descargar/<int:archivo_id>", methods=["GET"])
def descargar_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)
    inline = request.args.get("inline", "false").lower() == "true"

    return send_from_directory(
        current_app.config["CARPETA_SUBIDAS"],
        archivo.nombre_hash,
        as_attachment=not inline,
        download_name=archivo.nombre_original,
    )
