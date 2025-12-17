import os

from flask import current_app as app

from models import Archivo, Carpeta


# --- Utilidades ---
def parsear_tamano(cadena_tamano):
    """Parsea 'MB' a 'bytes' (float)"""
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
    """Formatea 'bytes' a 'string' legible"""
    for unidad in ["Bytes", "KB", "MB", "GB", "TB"]:
        if valor < 1024:
            return f"{valor:.2f} {unidad}"
        valor /= 1024
    return f"{valor:.2f} TB"


def obtener_tamano_carpeta(id_carpeta):
    """Calcula recursivamente el tamaño de una carpeta"""
    total = 0.0

    # Archivos directos
    archivos = Archivo.query.filter_by(carpeta_id=id_carpeta).all()
    for archivo in archivos:
        total += parsear_tamano(archivo.tamano)

    # Subcarpetas
    subcarpetas = Carpeta.query.filter_by(carpeta_padre_id=id_carpeta).all()
    for subcarpeta in subcarpetas:
        total += obtener_tamano_carpeta(subcarpeta.id)

    return total


def detectar_tipo_archivo(nombre_archivo):
    """Detecta el tipo de archivo por extensión para mejor previsualización"""
    if not nombre_archivo:
        return "otro"

    nombre = nombre_archivo.lower()

    # PDF
    if nombre.endswith(".pdf"):
        return "pdf"

    # Imágenes
    if any(nombre.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp", ".ico"]):
        return "imagen"

    # Videos
    if any(nombre.endswith(ext) for ext in [".mp4", ".mov", ".avi", ".webm", ".mkv", ".flv", ".wmv"]):
        return "video"

    # Audio
    if any(nombre.endswith(ext) for ext in [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".aac"]):
        return "audio"

    # Markdown
    if nombre.endswith(".md"):
        return "markdown"

    # CSV
    if nombre.endswith(".csv"):
        return "csv"

    # JSON
    if nombre.endswith(".json"):
        return "json"

    # Office Documents (Word)
    if any(nombre.endswith(ext) for ext in [".doc", ".docx", ".rtf", ".odt"]):
        return "word"

    # Office Documents (Excel)
    if any(nombre.endswith(ext) for ext in [".xls", ".xlsx", ".ods"]):
        return "excel"

    # Office Documents (PowerPoint)
    if any(nombre.endswith(ext) for ext in [".ppt", ".pptx", ".odp"]):
        return "powerpoint"

    # Código
    if any(
        nombre.endswith(ext)
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
            ".sql",
            ".sh",
            ".bat",
            ".ps1",
            ".xml",
            ".yaml",
            ".yml",
            ".ini",
            ".conf",
        ]
    ):
        return "codigo"

    # Archivos comprimidos
    if any(nombre.endswith(ext) for ext in [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"]):
        return "archivo"

    # Texto plano por defecto si no es nada de lo anterior pero parece texto
    if any(nombre.endswith(ext) for ext in [".txt", ".log"]):
        return "texto"

    return "otro"


def borrar_fisicos(carpeta_obj):
    """Función recursiva para borrar físicos"""
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
    """Recursivamente agrega archivos y subcarpetas al ZIP"""
    # Ruta actual en el ZIP
    ruta_carpeta = os.path.join(ruta_base, carpeta_obj.nombre) if ruta_base else carpeta_obj.nombre

    # Agregar archivos de esta carpeta
    for archivo in carpeta_obj.archivos:
        ruta_archivo = os.path.join(app.config["UPLOAD_FOLDER"], archivo.nombre_hash)

        if os.path.exists(ruta_archivo):
            # Agregar con la ruta completa en el ZIP
            nombre_archivo = os.path.join(ruta_carpeta, archivo.nombre_original)
            archivo_zip.write(ruta_archivo, arcname=nombre_archivo)

    # Agregar subcarpetas recursivamente
    for subcarpeta in carpeta_obj.subcarpetas:
        agregar_carpeta_a_zip(archivo_zip, subcarpeta, ruta_carpeta)


def obtener_estadisticas_carpeta(id_carpeta):
    """Devuelve estadísticas completas de una carpeta incluyendo subcarpetas."""
    total_carpetas = 0
    total_archivos = 0
    total_bytes = 0
    tipos = {}

    def recorrer(id_actual):
        nonlocal total_carpetas, total_archivos, total_bytes

        # Subcarpetas directas
        subcarpetas = Carpeta.query.filter_by(carpeta_padre_id=id_actual).all()

        for c in subcarpetas:
            tamano_bytes = obtener_tamano_carpeta(c.id)
            total_bytes += tamano_bytes

        total_carpetas += len(subcarpetas)

        # Archivos directos
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
