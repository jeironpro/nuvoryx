from flask import Blueprint, abort, render_template, request
from flask_login import current_user

from models import Archivo, Carpeta
from utils.utilidades import (
    detectar_tipo_archivo,
    formatear_tamano,
    obtener_estadisticas_carpeta,
    obtener_tamano_carpeta,
    parsear_tamano,
)

principal_bp = Blueprint("principal", __name__)


@principal_bp.route("/", methods=["GET"])
def indice():
    carpeta_id = request.args.get("carpeta_id", type=int)

    carpeta_actual = None
    ruta_migas = []

    total_uso_bytes = 0.0
    estadisticas_globales = None
    estadisticas_carpeta = None

    if carpeta_id:
        estadisticas_carpeta = obtener_estadisticas_carpeta(carpeta_id)
        carpeta_actual = Carpeta.query.get_or_404(carpeta_id)

        if current_user.is_authenticated and carpeta_actual.usuario_id and carpeta_actual.usuario_id != current_user.id:
            abort(403)

        temporal = carpeta_actual
        while temporal:
            ruta_migas.insert(0, {"id": temporal.id, "nombre": temporal.nombre})
            temporal = temporal.padre if hasattr(temporal, "padre") else None

        total_uso_bytes = obtener_tamano_carpeta(carpeta_id)
    else:
        if current_user.is_authenticated:
            total_carpetas = Carpeta.query.filter_by(usuario_id=current_user.id).count()
            carpetas_raiz = Carpeta.query.filter_by(carpeta_padre_id=None, usuario_id=current_user.id).all()
        else:
            total_carpetas = 0
            carpetas_raiz = []

        for c in carpetas_raiz:
            total_uso_bytes += obtener_tamano_carpeta(c.id)

        if current_user.is_authenticated:
            archivos_raiz = Archivo.query.filter_by(carpeta_id=None, usuario_id=current_user.id).all()
        else:
            archivos_raiz = []

        for a in archivos_raiz:
            total_uso_bytes += parsear_tamano(a.tamano)

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

    if carpeta_id:
        carpetas_query = Carpeta.query.filter_by(carpeta_padre_id=carpeta_id).order_by(Carpeta.nombre).all()
        archivos = Archivo.query.filter_by(carpeta_id=carpeta_id).order_by(Archivo.nombre_original.asc()).all()
    else:
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

    carpetas = []
    for c in carpetas_query:
        tamano_bytes = obtener_tamano_carpeta(c.id)
        carpetas.append(
            {
                "id": c.id,
                "nombre": c.nombre,
                "fecha_creacion": c.fecha_creacion,
                "fecha_actualizacion": c.fecha_actualizacion,
                "tamano": formatear_tamano(tamano_bytes),
            }
        )

    lista_archivos = []
    for archivo in archivos:
        lista_archivos.append(
            {
                "id": archivo.id,
                "nombre": archivo.nombre_original,
                "tipo": archivo.tipo,
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
