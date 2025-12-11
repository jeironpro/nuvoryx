import io
import os
import uuid
import zipfile

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, redirect, render_template, request, send_file, send_from_directory, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

from models import Archivo, Carpeta, Usuario, db
from utils.token import generar_token_confirmacion, verificar_token_confirmacion
from utils.utils import (
    agregar_carpeta_a_zip,
    borrar_fisicos,
    detectar_tipo_archivo,
    formatear_tamano,
    obtener_estadisticas_carpeta,
    obtener_tamano_carpeta,
    parsear_tamano,
)

# Cargar variables de entorno
load_dotenv()

# Inicializar la aplicación
app = Flask(__name__)

# Configuración de la base de datos
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("TRACK_MODIFICATIONS")

# Inicializar BD
db.init_app(app)

# Configuración de la carpeta de subida
app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER")

# Configuración del tamaño máximo de subida
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH"))

# Configuración de la clave secreta
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Configuración de la clave de seguridad
app.config["SECURITY_PASSWORD_SALT"] = os.getenv("SECURITY_PASSWORD_SALT")

# Configuración del correo
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT"))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

# Inicializar correo
mail = Mail(app)

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "index"  # Redirect to home if not logged in


@login_manager.user_loader
def cargar_usuario(usuario_id):
    return Usuario.query.get(int(usuario_id))


def enviar_correo_confirmacion(correo, token):
    """Envía un correo de confirmación"""
    enlace = f"http://localhost:5005/confirmar/{token}"

    mensaje = Message("Confirma tu cuenta", sender=app.config["MAIL_DEFAULT_SENDER"], recipients=[correo])

    mensaje.body = f"""
    Hola!
    Por favor, confirma tu cuenta haciendo clic en el siguiente enlace: {enlace}

    Gracias por usar Nuvoryx!"""

    mail.send(mensaje)


@app.route("/", methods=["GET"])
def index():
    carpeta_id = request.args.get("carpeta_id", type=int)

    # Obtener carpeta actual y ruta de migas
    carpeta_actual = None
    ruta_migas = []

    total_uso_bytes = 0.0
    estadisticas_globales = None
    estadisticas_carpeta = None

    if carpeta_id:
        estadisticas_carpeta = obtener_estadisticas_carpeta(carpeta_id)
        carpeta_actual = Carpeta.query.get_or_404(carpeta_id)

        # Verificar que la carpeta pertenece al usuario autenticado (si está autenticado)
        if current_user.is_authenticated and carpeta_actual.usuario_id and carpeta_actual.usuario_id != current_user.id:
            abort(403)  # Forbidden

        # Construir ruta de migas
        temporal = carpeta_actual
        while temporal:
            ruta_migas.insert(0, {"id": temporal.id, "nombre": temporal.nombre})
            # Asume que el modelo Carpeta tiene una relación 'padre'
            # o similar para el objeto padre
            temporal = temporal.padre if hasattr(temporal, "padre") else None

        # Calcular el tamaño de la carpeta actual
        total_uso_bytes = obtener_tamano_carpeta(carpeta_id)
    else:
        # Raíz: Calcular estadísticas globales
        if current_user.is_authenticated:
            # Usuario autenticado: contar solo sus carpetas
            total_carpetas = Carpeta.query.filter_by(usuario_id=current_user.id).count()
            carpetas_raiz = Carpeta.query.filter_by(carpeta_padre_id=None, usuario_id=current_user.id).all()
        else:
            # Usuario no autenticado: contar carpetas sin usuario asignado
            total_carpetas = 0
            carpetas_raiz = []

        for c in carpetas_raiz:
            total_uso_bytes += obtener_tamano_carpeta(c.id)

        # Archivos raíz
        if current_user.is_authenticated:
            archivos_raiz = Archivo.query.filter_by(carpeta_id=None, usuario_id=current_user.id).all()
        else:
            archivos_raiz = []

        for a in archivos_raiz:
            total_uso_bytes += parsear_tamano(a.tamano)

        # Tipo más común global
        if current_user.is_authenticated:
            todos_archivos = Archivo.query.filter_by(usuario_id=current_user.id).all()
        else:
            todos_archivos = []

        contador_tipos = {}
        for a in todos_archivos:
            tipo = detectar_tipo_archivo(a.nombre_original)
            contador_tipos[tipo] = contador_tipos.get(tipo, 0) + 1

        tipo_mas_comun = "-"
        if contador_tipos:
            tipo_mas_comun = max(contador_tipos, key=contador_tipos.get)
            if tipo_mas_comun == "hoja_calculo":
                tipo_mas_comun = "Hoja de cálculo"
            elif tipo_mas_comun == "presentacion":
                tipo_mas_comun = "Presentación"
            else:
                tipo_mas_comun = tipo_mas_comun.capitalize()

        estadisticas_globales = {
            "total_carpetas": total_carpetas,
            "total_archivos": len(todos_archivos),
            "espacio_usado": formatear_tamano(total_uso_bytes),
            "tipo_comun": tipo_mas_comun,
        }

    # Obtener carpetas y archivos según contexto
    if carpeta_id:
        # Dentro de una carpeta: mostrar subcarpetas y archivos de esa carpeta
        # Revisar propietario de la carpeta padre.
        # Subelementos son accesibles si el padre es accesible.
        carpetas_query = Carpeta.query.filter_by(carpeta_padre_id=carpeta_id).order_by(Carpeta.nombre).all()
        archivos = Archivo.query.filter_by(carpeta_id=carpeta_id).order_by(Archivo.nombre_original.asc()).all()
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
                Carpeta.query.filter_by(carpeta_padre_id=None, usuario_id=None).order_by(Carpeta.nombre).all()
            )
            archivos = (
                Archivo.query.filter_by(carpeta_id=None, usuario_id=None).order_by(Archivo.nombre_original.asc()).all()
            )

    # Procesar carpetas con tamaño
    carpetas = []
    for c in carpetas_query:
        tamano_bytes = obtener_tamano_carpeta(c.id)
        carpetas.append(
            {
                "id": c.id,
                "nombre": c.nombre,
                "fecha_creacion": c.fecha_creacion,
                "tamano": formatear_tamano(tamano_bytes),
            }
        )

    # Sumar el tamaño de las carpetas a la estadística de la carpeta actual
    if estadisticas_carpeta:
        tamano_carpetas = sum([float(carpeta["tamano"][:-3]) for carpeta in carpetas])
        espacio_carpeta = float(estadisticas_carpeta["espacio_usado"].split(" ")[0])
        estadisticas_carpeta["espacio_usado"] = espacio_carpeta + tamano_carpetas

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
            }
        )
    return render_template(
        "index.html",
        archivos=lista_archivos,
        carpetas=carpetas,
        carpeta_actual=carpeta_actual,
        ruta_migas=ruta_migas,
        estadisticas_globales=estadisticas_globales,
        estadisticas_carpeta=estadisticas_carpeta,
        current_user=current_user,
    )


# --- RUTAS DE AUTENTICACIÓN ---
@app.route("/enviar_confirmacion/<correo>")
def enviar_confirmacion(correo):
    token = generar_token_confirmacion(correo)
    enviar_correo_confirmacion(correo, token)
    return jsonify({"success": "Correo enviado"}), 200


@app.route("/registro", methods=["POST"])
def registro():
    datos = request.get_json()
    nombre = datos.get("nombre")
    correo = datos.get("email")
    contrasena = datos.get("password")

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


@app.route("/confirmar/<token>")
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
        return redirect(url_for("index"))
    else:
        return redirect(url_for("index"))


@app.route("/inicio_sesion", methods=["POST"])
def inicio_sesion():
    datos = request.get_json()
    correo = datos.get("email")
    contrasena = datos.get("password")

    if not correo or not contrasena:
        return jsonify({"error": "Email y contraseña son requeridos"}), 400

    # Buscar usuario
    usuario = Usuario.query.filter_by(correo=correo).first()

    if not usuario or not usuario.verificar_contrasena(contrasena):
        return jsonify({"error": "Credenciales incorrectas"}), 401

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


@app.route("/cerrar_sesion", methods=["POST"])
@login_required
def cerrar_sesion():
    logout_user()
    return jsonify({"success": True})


@app.route("/crear-carpeta", methods=["POST"])
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
    db.session.commit()

    return jsonify({"success": True, "id": nueva_carpeta.id, "nombre": nueva_carpeta.nombre})


@app.route("/subir", methods=["POST"])
@login_required
def subir_archivo():
    if "archivos" not in request.files:
        return jsonify({"error": "No file part"}), 400

    archivos = request.files.getlist("archivos")
    carpeta_id = request.form.get("carpeta_id", type=int)
    archivos_guardados = []

    for archivo in archivos:
        if archivo.filename == "":
            continue

        nombre_archivo = secure_filename(archivo.filename)
        extension_archivo = os.path.splitext(nombre_archivo)[1].lower()

        # Generar nombre hash seguro
        nombre_hash = f"{uuid.uuid4().hex}{extension_archivo}"
        ruta_archivo = os.path.join(app.config["UPLOAD_FOLDER"], nombre_hash)

        # Guardar en disco
        archivo.save(ruta_archivo)

        # Calcular tamaño (simulado o real si se lee antes, aquí usamos os.stat tras guardar)
        tamano_bytes = os.path.getsize(ruta_archivo)

        # Formatear tamaño
        if tamano_bytes < 1024:
            tamano_str = f"{tamano_bytes} B"
        elif tamano_bytes < 1024 * 1024:
            tamano_str = f"{tamano_bytes / 1024:.1f} KB"
        else:
            tamano_str = f"{tamano_bytes / (1024 * 1024):.1f} MB"

        # Determinar tipo simple para iconos
        tipo_simple = "otro"
        if extension_archivo in [".pdf"]:
            tipo_simple = "pdf"
        elif extension_archivo in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
            tipo_simple = "imagen"
        elif extension_archivo in [".mp4", ".mov", ".avi", ".webm"]:
            tipo_simple = "video"

        # Guardar en BD
        usuario_id = current_user.id if current_user.is_authenticated else None

        nuevo_archivo = Archivo(
            nombre_original=nombre_archivo,
            nombre_hash=nombre_hash,
            tipo=tipo_simple,
            tamano=tamano_str,
            carpeta_id=carpeta_id,
            usuario_id=usuario_id,
        )
        db.session.add(nuevo_archivo)
        db.session.commit()

        archivos_guardados.append(
            {
                "id": nuevo_archivo.id,
                "nombre": nombre_archivo,
                "status": "success",
            }
        )

    return jsonify({"message": "Archivos subidos", "archivos": archivos_guardados}), 200


@app.route("/eliminar/<int:archivo_id>", methods=["DELETE"])
def eliminar_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)

    # Eliminar del disco
    ruta_archivo = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)
    try:
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)
    except Exception as e:
        print(f"Error eliminando archivo {ruta_archivo}: {e}")

    db.session.delete(archivo)
    db.session.commit()

    return jsonify({"success": True})


@app.route("/eliminar-carpeta/<int:carpeta_id>", methods=["DELETE"])
def eliminar_carpeta_route(carpeta_id):
    carpeta = Carpeta.query.get_or_404(carpeta_id)

    borrar_fisicos(carpeta)
    db.session.delete(carpeta)
    db.session.commit()

    return jsonify({"success": True})


@app.route("/eliminar-multiples", methods=["POST"])
def eliminar_multiples():
    data = request.get_json()
    ids = data.get("ids", [])

    if not ids:
        return jsonify({"error": "No IDs proporcionados"}), 400

    exitos = 0
    errores = 0

    for archivo_id in ids:
        archivo = Archivo.query.get(archivo_id)
        if archivo:
            # Eliminar del disco
            ruta_archivo = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)
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
            # Aquí idealmente deberíamos eliminar recursivamente
            # los archivos físicos dentro. Por simplicidad delegamos
            # en cascade delete de la BD para los registros.

            borrar_fisicos(carpeta)
            db.session.delete(carpeta)
            exitos += 1

    db.session.commit()
    return jsonify({"success": True, "deleted": exitos, "errors": errores})


@app.route("/descargar-zip", methods=["POST"])
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
                    ruta_archivo = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)

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


@app.route("/descargar-carpeta/<int:carpeta_id>", methods=["GET"])
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


@app.route("/descargar/<int:archivo_id>", methods=["GET"])
def descargar_archivo(archivo_id):
    archivo = Archivo.query.get_or_404(archivo_id)

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        archivo.nombre_hash,
        as_attachment=True,
        download_name=archivo.nombre_original,
    )


if __name__ == "__main__":
    # Crear tablas solo cuando se ejecuta directamente
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5555)
