import io
import os
import uuid
import zipfile

from flask import Flask, abort, jsonify, render_template, request, send_file, send_from_directory
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename

from models import Archivo, Carpeta, Usuario, db

app = Flask(__name__)

# Configuración
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:jeironpro@localhost/nuvoryx"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024
app.config["SECRET_KEY"] = "nuvoryx-secret-key-change-in-production"  # Cambiar en producción

# Inicializar BD
db.init_app(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "root"  # Redirect to home if not logged in


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# --- HELPERS ---
def parse_size(size_str):
    """Parsea '1.5 MB' a bytes (float)"""
    if not size_str:
        return 0.0
    try:
        parts = size_str.split()
        if len(parts) < 2:
            return 0.0
        val = float(parts[0].replace(",", "."))
        unit = parts[1].upper()

        factors = {
            "B": 1,
            "BYTES": 1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4,
        }
        return val * factors.get(unit, 1)
    except Exception:
        return 0.0


def format_size(bytes_val):
    """Formatea bytes a string legible"""
    for unit in ["Bytes", "KB", "MB", "GB", "TB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} TB"


def get_folder_size(folder_id):
    """Calcula recursivamente el tamaño de una carpeta"""
    total = 0.0
    # Archivos directos
    files = Archivo.query.filter_by(carpeta_id=folder_id).all()
    for f in files:
        total += parse_size(f.tamano)

    # Subcarpetas
    subfolders = Carpeta.query.filter_by(carpeta_padre_id=folder_id).all()
    for sub in subfolders:
        total += get_folder_size(sub.id)

    return total


def detectar_tipo_archivo(nombre):
    """Detecta el tipo de archivo por extensión (replica lógica de utils.js)"""
    if not nombre:
        return "otro"

    n = nombre.lower()

    # PDF
    if n.endswith(".pdf"):
        return "pdf"

    # Imágenes
    if any(
        n.endswith(ext)
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico"]
    ):
        return "imagen"

    # Videos
    if any(n.endswith(ext) for ext in [".mp4", ".mov", ".avi", ".webm", ".mkv", ".flv", ".wmv"]):
        return "video"

    # Audio
    if any(n.endswith(ext) for ext in [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"]):
        return "audio"

    # Documentos
    if any(n.endswith(ext) for ext in [".doc", ".docx", ".txt", ".rtf", ".odt"]):
        return "documento"

    # Hojas de cálculo
    if any(n.endswith(ext) for ext in [".xls", ".xlsx", ".csv", ".ods"]):
        return "hoja_calculo"

    # Presentaciones
    if any(n.endswith(ext) for ext in [".ppt", ".pptx", ".odp"]):
        return "presentacion"

    # Archivos comprimidos
    if any(n.endswith(ext) for ext in [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]):
        return "archivo"

    # Código
    if any(
        n.endswith(ext)
        for ext in [
            ".html",
            ".css",
            ".js",
            ".jsx",
            ".ts",
            ".tsx",
            ".py",
            ".java",
            ".c",
            ".cpp",
            ".php",
            ".rb",
            ".go",
            ".rs",
        ]
    ):
        return "codigo"

    return "otro"


@app.route("/", methods=["GET"])
def root():
    carpeta_id = request.args.get("carpeta_id", type=int)

    # Obtener carpeta actual y ruta de migas
    carpeta_actual = None
    ruta_migas = []

    total_usage_bytes = 0.0
    global_stats = None

    if carpeta_id:
        carpeta_actual = Carpeta.query.get_or_404(carpeta_id)

        # Verificar que la carpeta pertenece al usuario autenticado (si está autenticado)
        if (
            current_user.is_authenticated
            and carpeta_actual.usuario_id
            and carpeta_actual.usuario_id != current_user.id
        ):
            abort(403)  # Forbidden

        # Construir ruta de migas
        temp = carpeta_actual
        while temp:
            ruta_migas.insert(0, {"id": temp.id, "nombre": temp.nombre})
            # Assuming Carpeta model has a 'padre' relationship
            # or similar for parent object
            temp = temp.padre if hasattr(temp, "padre") else None

        # Calcular tamaño de la carpeta actual
        total_usage_bytes = get_folder_size(carpeta_id)
    else:
        # Root: Calcular estadísticas globales
        if current_user.is_authenticated:
            # Usuario autenticado: contar solo sus carpetas
            total_carpetas = Carpeta.query.filter_by(
                carpeta_padre_id=None, usuario_id=current_user.id
            ).count()
            carpetas_raiz = Carpeta.query.filter_by(
                carpeta_padre_id=None, usuario_id=current_user.id
            ).all()
        else:
            # Usuario no autenticado: contar carpetas sin usuario asignado
            total_carpetas = Carpeta.query.filter_by(carpeta_padre_id=None, usuario_id=None).count()
            carpetas_raiz = Carpeta.query.filter_by(carpeta_padre_id=None, usuario_id=None).all()

        for c in carpetas_raiz:
            total_usage_bytes += get_folder_size(c.id)

        # Archivos raíz
        if current_user.is_authenticated:
            archivos_raiz = Archivo.query.filter_by(
                carpeta_id=None, usuario_id=current_user.id
            ).all()
        else:
            archivos_raiz = Archivo.query.filter_by(carpeta_id=None, usuario_id=None).all()

        for a in archivos_raiz:
            total_usage_bytes += parse_size(a.tamano)

        # Tipo más común global
        if current_user.is_authenticated:
            todos_archivos = Archivo.query.filter_by(usuario_id=current_user.id).all()
        else:
            todos_archivos = Archivo.query.filter_by(usuario_id=None).all()

        tipos_count = {}
        for a in todos_archivos:
            tipo = detectar_tipo_archivo(a.nombre_original)
            tipos_count[tipo] = tipos_count.get(tipo, 0) + 1

        tipo_mas_comun = "-"
        if tipos_count:
            tipo_mas_comun = max(tipos_count, key=tipos_count.get)
            if tipo_mas_comun == "hoja_calculo":
                tipo_mas_comun = "Hoja de cálculo"
            elif tipo_mas_comun == "presentacion":
                tipo_mas_comun = "Presentación"
            else:
                tipo_mas_comun = tipo_mas_comun.capitalize()

        global_stats = {
            "total_carpetas": total_carpetas,
            "espacio_usado": format_size(total_usage_bytes),
            "tipo_comun": tipo_mas_comun,
        }

    formatted_total_usage = format_size(total_usage_bytes)

    # Obtener carpetas y archivos según contexto
    if carpeta_id:
        # Dentro de una carpeta: mostrar subcarpetas y archivos de esa carpeta
        # Ownership check for parent folder is done above.
        # Sub-items are assumed to be accessible if parent is accessible.
        carpetas_query = (
            Carpeta.query.filter_by(carpeta_padre_id=carpeta_id).order_by(Carpeta.nombre).all()
        )
        archivos = (
            Archivo.query.filter_by(carpeta_id=carpeta_id)
            .order_by(Archivo.nombre_original.asc())
            .all()
        )
    else:
        # Raíz: mostrar carpetas y archivos raíz del usuario
        if current_user.is_authenticated:
            carpetas_query = (
                Carpeta.query.filter_by(carpeta_padre_id=None, usuario_id=current_user.id)
                .order_by(Carpeta.nombre)
                .all()
            )
            archivos = (
                Archivo.query.filter_by(carpeta_id=None, usuario_id=current_user.id)
                .order_by(Archivo.nombre_original.asc())
                .all()
            )
        else:
            carpetas_query = (
                Carpeta.query.filter_by(carpeta_padre_id=None, usuario_id=None)
                .order_by(Carpeta.nombre)
                .all()
            )
            archivos = (
                Archivo.query.filter_by(carpeta_id=None, usuario_id=None)
                .order_by(Archivo.nombre_original.asc())
                .all()
            )

    # Procesar carpetas con tamaño
    carpetas = []
    for c in carpetas_query:
        size_bytes = get_folder_size(c.id)
        carpetas.append(
            {
                "id": c.id,
                "nombre": c.nombre,
                "fecha_creacion": c.fecha_creacion,
                "tamano": format_size(size_bytes),
                "usuario": {
                    "nombre": c.usuario_nombre,
                    "avatar_url": c.usuario_avatar,
                    "email": c.usuario_email,
                },
            }
        )

    # Formatear la respuesta para la plantilla
    lista_archivos = []
    for archivo in archivos:
        lista_archivos.append(
            {
                "id": archivo.id,
                "nombre": archivo.nombre_original,
                "tipo": archivo.tipo,  # extension/mime simplificada
                "tamano": archivo.tamano,
                "fecha_subida": archivo.fecha_subida,
                "usuario": {
                    "nombre": archivo.usuario_nombre,
                    "avatar_url": archivo.usuario_avatar,
                    "email": archivo.usuario_email,
                },
            }
        )
    return render_template(
        "index.html",
        archivos=lista_archivos,
        carpetas=carpetas,
        carpeta_actual=carpeta_actual,
        ruta_migas=ruta_migas,
        total_usage=formatted_total_usage,
        global_stats=global_stats,
        current_user=current_user,
    )


@app.route("/crear-carpeta", methods=["POST"])
def crear_carpeta():
    nombre = request.form.get("nombre")
    carpeta_padre_id = request.form.get("carpeta_padre_id", type=int)

    if not nombre:
        return jsonify({"error": "Nombre requerido"}), 400

    # Asignar usuario_id si está autenticado
    usuario_id = current_user.id if current_user.is_authenticated else None

    nueva_carpeta = Carpeta(nombre=nombre, carpeta_padre_id=carpeta_padre_id, usuario_id=usuario_id)
    db.session.add(nueva_carpeta)
    db.session.commit()

    return jsonify({"success": True, "id": nueva_carpeta.id, "nombre": nueva_carpeta.nombre})


@app.route("/subir", methods=["POST"])
def subir_archivo():
    if "archivos" not in request.files:
        return jsonify({"error": "No file part"}), 400

    files = request.files.getlist("archivos")
    carpeta_id = request.form.get("carpeta_id", type=int)
    saved_files = []

    for file in files:
        if file.filename == "":
            continue

        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()

        # Generar nombre hash seguro
        nombre_hash = f"{uuid.uuid4().hex}{file_ext}"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], nombre_hash)

        # Guardar en disco
        file.save(filepath)

        # Calcular tamaño (simulado o real si se lee antes, aquí usamos os.stat tras guardar)
        size_bytes = os.path.getsize(filepath)

        # Formatear tamaño
        if size_bytes < 1024:
            tamano_str = f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            tamano_str = f"{size_bytes / 1024:.1f} KB"
        else:
            tamano_str = f"{size_bytes / (1024 * 1024):.1f} MB"

        # Determinar tipo simple para iconos
        tipo_simple = "otro"
        if file_ext in [".pdf"]:
            tipo_simple = "pdf"
        elif file_ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            tipo_simple = "imagen"
        elif file_ext in [".mp4", ".mov", ".avi", ".webm"]:
            tipo_simple = "video"

        # Guardar en BD
        usuario_id = current_user.id if current_user.is_authenticated else None

        nuevo_archivo = Archivo(
            nombre_original=filename,
            nombre_hash=nombre_hash,
            tipo=tipo_simple,
            tamano=tamano_str,
            carpeta_id=carpeta_id,
            usuario_id=usuario_id,
        )
        db.session.add(nuevo_archivo)
        db.session.commit()

        saved_files.append({"id": nuevo_archivo.id, "nombre": filename, "status": "success"})

    return jsonify({"message": "Archivos subidos", "archivos": saved_files}), 200


@app.route("/eliminar/<int:archivo_id>", methods=["DELETE"])
def eliminar_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)

    # Eliminar del disco
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        print(f"Error removing file {filepath}: {e}")

    db.session.delete(archivo)
    db.session.commit()

    return jsonify({"success": True})


@app.route("/eliminar-carpeta/<int:carpeta_id>", methods=["DELETE"])
def eliminar_carpeta_route(carpeta_id):
    carpeta = Carpeta.query.get_or_404(carpeta_id)

    # Helper recursivo para borrar físicos (duplicado de lógica, idealmente refactorizar)
    def borrar_fisicos(carpeta_obj):
        for sub in carpeta_obj.subcarpetas:
            borrar_fisicos(sub)
        for arch in carpeta_obj.archivos:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], arch.nombre_hash)
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    borrar_fisicos(carpeta)
    db.session.delete(carpeta)
    db.session.commit()

    return jsonify({"success": True})


@app.route("/eliminar-multiples", methods=["POST"])
def eliminar_multiples():
    data = request.get_json()
    ids = data.get("ids", [])

    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    exitos = 0
    errores = 0

    for archivo_id in ids:
        archivo = Archivo.query.get(archivo_id)
        if archivo:
            # Eliminar del disco
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)
            try:
                if os.path.exists(filepath):
                    os.remove(filepath)
            except Exception as e:
                print(f"Error removing file {filepath}: {e}")
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
            # Aquí idealmente deberíamos eliminar recursivamente
            # los archivos físicos dentro. Por simplicidad delegamos
            # en cascade delete de la BD para los registros.

            # Helper recursivo para borrar físicos
            def borrar_fisicos(carpeta_obj):
                for sub in carpeta_obj.subcarpetas:
                    borrar_fisicos(sub)
                for arch in carpeta_obj.archivos:
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], arch.nombre_hash)
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                        except Exception:
                            pass

            borrar_fisicos(carpeta)
            db.session.delete(carpeta)
            exitos += 1

    db.session.commit()
    return jsonify({"success": True, "deleted": exitos, "errors": errores})


@app.route("/descargar-zip", methods=["POST"])
def descargar_zip():
    # Obtener IDs del formulario (si se usa form submit) o JSON
    if request.is_json:
        data = request.get_json()
        ids = data.get("ids", [])
    else:
        # Si viene de un formulario tradicional (hidden inputs)
        ids = request.form.getlist("ids[]")

    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    # Crear buffer en memoria para el ZIP
    memory_file = io.BytesIO()

    try:
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
            for archivo_id in ids:
                archivo = Archivo.query.get(archivo_id)
                if archivo:
                    filepath = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)
                    if os.path.exists(filepath):
                        # Añadir al zip con el nombre original
                        # Manejo de duplicados de nombre en el zip podría requerir lógica extra,
                        # pero por simplicidad usaremos nombre original
                        zf.write(filepath, arcname=archivo.nombre_original)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    memory_file.seek(0)

    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name="archivos_descargados.zip",
    )


@app.route("/descargar-carpeta/<int:carpeta_id>", methods=["GET"])
def descargar_carpeta(carpeta_id):
    carpeta = Carpeta.query.get_or_404(carpeta_id)

    # Crear buffer en memoria para el ZIP
    memory_file = io.BytesIO()

    def agregar_carpeta_a_zip(zf, carpeta_obj, ruta_base=""):
        """Recursivamente agrega archivos y subcarpetas al ZIP"""
        # Ruta actual en el ZIP
        ruta_carpeta = (
            os.path.join(ruta_base, carpeta_obj.nombre) if ruta_base else carpeta_obj.nombre
        )

        # Agregar archivos de esta carpeta
        for archivo in carpeta_obj.archivos:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)
            if os.path.exists(filepath):
                # Agregar con la ruta completa en el ZIP
                arcname = os.path.join(ruta_carpeta, archivo.nombre_original)
                zf.write(filepath, arcname=arcname)

        # Agregar subcarpetas recursivamente
        for subcarpeta in carpeta_obj.subcarpetas:
            agregar_carpeta_a_zip(zf, subcarpeta, ruta_carpeta)

    try:
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zf:
            agregar_carpeta_a_zip(zf, carpeta)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    memory_file.seek(0)

    # Nombre del archivo ZIP
    zip_filename = f"{carpeta.nombre}.zip"

    return send_file(
        memory_file, mimetype="application/zip", as_attachment=True, download_name=zip_filename
    )


@app.route("/descargar/<int:archivo_id>", methods=["GET"])
def descargar_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        archivo.nombre_hash,
        as_attachment=True,
        download_name=archivo.nombre_original,
    )


# --- AUTHENTICATION ROUTES ---


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")
    password = data.get("password")

    # Validación
    if not nombre or not email or not password:
        return jsonify({"error": "Todos los campos son requeridos"}), 400

    if len(password) < 6:
        return jsonify({"error": "La contraseña debe tener al menos 6 caracteres"}), 400

    # Verificar si el email ya existe
    if Usuario.query.filter_by(email=email).first():
        return jsonify({"error": "El email ya está registrado"}), 400

    # Crear nuevo usuario
    nuevo_usuario = Usuario(nombre=nombre, email=email)
    nuevo_usuario.set_password(password)

    db.session.add(nuevo_usuario)
    db.session.commit()

    # Auto-login después del registro
    login_user(nuevo_usuario)

    return jsonify(
        {
            "success": True,
            "usuario": {
                "id": nuevo_usuario.id,
                "nombre": nuevo_usuario.nombre,
                "email": nuevo_usuario.email,
            },
        }
    )


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    # Buscar usuario
    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not usuario.check_password(password):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    # Login exitoso
    login_user(usuario)
    usuario.ultimo_acceso = db.func.now()
    db.session.commit()

    return jsonify(
        {
            "success": True,
            "usuario": {"id": usuario.id, "nombre": usuario.nombre, "email": usuario.email},
        }
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True})


if __name__ == "__main__":
    # Crear tablas solo cuando se ejecuta directamente
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5005)
