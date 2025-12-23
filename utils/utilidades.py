import os

from flask import current_app as app

from models import Archivo, Carpeta


def parsear_tamano(cadena_tamano):
    if not cadena_tamano:
        return 0.0
    try:
        partes = cadena_tamano.split()
        if len(partes) < 2:
            return 0.0

        valor = float(partes[0].replace(",", "."))
        unidad = partes[1].upper()

        factores = {
            "B": 1,
            "BYTES": 1,
            "KB": 1024,
            "MB": 1024**2,
            "GB": 1024**3,
            "TB": 1024**4,
        }
        return valor * factores.get(unidad, 1)
    except Exception:
        return 0.0


def formatear_tamano(valor):
    for unidad in ["Bytes", "KB", "MB", "GB", "TB"]:
        if valor < 1024:
            return f"{valor:.2f} {unidad}"
        valor /= 1024
    return f"{valor:.2f} TB"


def obtener_tamano_carpeta(id_carpeta):
    total = 0.0

    archivos = Archivo.query.filter_by(carpeta_id=id_carpeta).all()
    for archivo in archivos:
        total += parsear_tamano(archivo.tamano)

    subcarpetas = Carpeta.query.filter_by(carpeta_padre_id=id_carpeta).all()
    for subcarpeta in subcarpetas:
        total += obtener_tamano_carpeta(subcarpeta.id)

    return total


def detectar_tipo_archivo(nombre_archivo):
    if not nombre_archivo:
        return "otro"

    nombre = nombre_archivo.lower()

    nom_exactos = ["license", "readme", "procfile", "dockerfile", "makefile", ".env", ".gitignore", "docker-compose"]
    if nombre in nom_exactos or any(nombre.startswith(n + ".") for n in nom_exactos):
        return "texto"

    if nombre.endswith(".pdf"):
        return "pdf"

    ext_img = [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".svg",
        ".bmp",
        ".ico",
        ".tiff",
        ".tif",
        ".avif",
        ".heic",
        ".heif",
        ".fig",
    ]
    if any(nombre.endswith(ext) for ext in ext_img):
        return "imagen"

    ext_video = [".mp4", ".mov", ".avi", ".webm", ".mkv", ".flv", ".wmv", ".m4v", ".3gp", ".3g2", ".ogv"]
    if any(nombre.endswith(ext) for ext in ext_video):
        return "video"
    ext_audio = [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac", ".wma", ".opus"]
    if any(nombre.endswith(ext) for ext in ext_audio):
        return "audio"

    if nombre.endswith(".md") or nombre.endswith(".markdown"):
        return "markdown"

    if nombre.endswith(".csv"):
        return "csv"

    if nombre.endswith(".json"):
        return "json"

    if any(nombre.endswith(ext) for ext in [".doc", ".docx", ".rtf", ".odt", ".pages"]):
        return "word"

    if any(nombre.endswith(ext) for ext in [".xls", ".xlsx", ".ods", ".numbers"]):
        return "excel"

    if any(nombre.endswith(ext) for ext in [".ppt", ".pptx", ".odp", ".key"]):
        return "powerpoint"

    ext_codigo = [
        ".html",
        ".htm",
        ".xhtml",
        ".ejs",
        ".pug",
        ".haml",
        ".css",
        ".less",
        ".scss",
        ".sass",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".vue",
        ".svelte",
        ".py",
        ".pyw",
        ".ipynb",
        ".java",
        ".kt",
        ".kts",
        ".scala",
        ".gradle",
        ".c",
        ".cpp",
        ".cc",
        ".h",
        ".hpp",
        ".hh",
        ".cs",
        ".fs",
        ".php",
        ".rb",
        ".go",
        ".rs",
        ".pl",
        ".pm",
        ".t",
        ".sql",
        ".xml",
        ".yaml",
        ".yml",
        ".toml",
        ".ini",
        ".conf",
        ".dockerfile",
        ".env",
        ".gitignore",
        ".makefile",
        ".sh",
        ".bash",
        ".zsh",
        ".bat",
        ".cmd",
        ".ps1",
        ".r",
        ".rmd",
        ".jl",
        ".dart",
        ".lua",
        ".clj",
        ".ex",
        ".erl",
        ".hs",
        ".ml",
        ".pas",
        ".d",
        ".nim",
        ".zig",
    ]
    if any(nombre.endswith(ext) for ext in ext_codigo):
        return "codigo"

    if any(nombre.endswith(ext) for ext in [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".dmg"]):
        return "archivo"

    if any(nombre.endswith(ext) for ext in [".txt", ".log", ".tex", ".latex", ".ascii"]):
        return "texto"

    return "otro"


def borrar_fisicos(carpeta_obj):
    for subcarpeta in carpeta_obj.subcarpetas:
        borrar_fisicos(subcarpeta)

    for archivo in carpeta_obj.archivos:
        ruta_archivo = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)

        if os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
            except Exception:
                pass


def agregar_carpeta_a_zip(archivo_zip, carpeta_obj, ruta_base=""):
    ruta_carpeta = os.path.join(ruta_base, carpeta_obj.nombre) if ruta_base else carpeta_obj.nombre

    for archivo in carpeta_obj.archivos:
        ruta_archivo = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)

        if os.path.exists(ruta_archivo):
            nombre_archivo = os.path.join(ruta_carpeta, archivo.nombre_original)
            archivo_zip.write(ruta_archivo, arcname=nombre_archivo)

    for subcarpeta in carpeta_obj.subcarpetas:
        agregar_carpeta_a_zip(archivo_zip, subcarpeta, ruta_carpeta)


def obtener_estadisticas_carpeta(id_carpeta):
    total_carpetas = 0
    total_archivos = 0
    total_bytes = 0
    tipos = {}

    def recorrer(id_actual):
        nonlocal total_carpetas, total_archivos, total_bytes

        subcarpetas = Carpeta.query.filter_by(carpeta_padre_id=id_actual).all()

        for c in subcarpetas:
            tamano_bytes = obtener_tamano_carpeta(c.id)
            total_bytes += tamano_bytes

        total_carpetas += len(subcarpetas)

        archivos = Archivo.query.filter_by(carpeta_id=id_actual).all()
        total_archivos += len(archivos)

        for a in archivos:
            peso = parsear_tamano(a.tamano)
            total_bytes += peso
            tipo = detectar_tipo_archivo(a.nombre_original)
            tipos[tipo] = tipos.get(tipo, 0) + 1

    recorrer(id_carpeta)

    tipo_comun = "-"
    if tipos:
        tipo_comun = max(tipos, key=tipos.get).capitalize()

    return {
        "total_carpetas": total_carpetas,
        "total_archivos": total_archivos,
        "espacio_usado": formatear_tamano(total_bytes),
        "tipo_comun": tipo_comun,
    }
