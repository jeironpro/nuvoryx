from datetime import datetime

import bcrypt
from flask_login import UserMixin

from extensiones import db


class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(255), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(255), default="account_circle")
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=False)

    # Relaciones
    archivos = db.relationship("Archivo", backref="propietario", lazy=True, foreign_keys="Archivo.usuario_id")
    carpetas = db.relationship("Carpeta", backref="propietario", lazy=True, foreign_keys="Carpeta.usuario_id")
    notificaciones = db.relationship("Notificacion", backref="usuario", lazy=True, cascade="all, delete-orphan")

    def codificar_contrasena(self, contrasena):
        """Codifica la contraseña usando bcrypt"""
        self.contrasena_hash = bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verificar_contrasena(self, contrasena):
        """Verifica la contraseña con el hash"""
        return bcrypt.checkpw(contrasena.encode("utf-8"), self.contrasena_hash.encode("utf-8"))

    def __repr__(self):
        return f"<Usuario {self.correo}>"


class Carpeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    carpeta_padre_id = db.Column(db.Integer, db.ForeignKey("carpeta.id"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow)

    subcarpetas = db.relationship("Carpeta", backref=db.backref("padre", remote_side=[id]), lazy=True)
    archivos = db.relationship("Archivo", backref="carpeta", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Carpeta {self.nombre}>"


class Archivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_original = db.Column(db.String(255), nullable=False)
    nombre_hash = db.Column(db.String(255), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=False)
    tamano = db.Column(db.String(50), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    carpeta_id = db.Column(db.Integer, db.ForeignKey("carpeta.id"), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    def __repr__(self):
        return f"<Archivo {self.nombre_original}>"


class Notificacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    mensaje = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    leida = db.Column(db.Boolean, default=False)
    tipo = db.Column(db.String(50), default="info")

    def __repr__(self):
        return f"<Notificacion {self.mensaje[:20]}...>"
