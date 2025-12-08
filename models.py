from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar_url = db.Column(db.String(255), default="account_circle")
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    archivos = db.relationship('Archivo', backref='propietario', lazy=True, foreign_keys='Archivo.usuario_id')
    carpetas = db.relationship('Carpeta', backref='propietario', lazy=True, foreign_keys='Carpeta.usuario_id')
    
    def set_password(self, password):
        """Hash password using bcrypt"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Carpeta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    carpeta_padre_id = db.Column(db.Integer, db.ForeignKey('carpeta.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Usuario info (hardcoded por ahora para compatibilidad, se usará usuario_id en el futuro)
    usuario_nombre = db.Column(db.String(100), default="Admin User")
    usuario_avatar = db.Column(db.String(255), default="account_circle")
    usuario_email = db.Column(db.String(255), default="admin@nuvoryx.com")
    
    # Relación con subcarpetas
    subcarpetas = db.relationship('Carpeta', 
        backref=db.backref('padre', remote_side=[id]),
        lazy=True
    )
    # Relación con archivos
    archivos = db.relationship('Archivo', backref='carpeta', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Carpeta {self.nombre}>'

class Archivo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_original = db.Column(db.String(255), nullable=False)
    nombre_hash = db.Column(db.String(255), nullable=False, unique=True)
    tipo = db.Column(db.String(50), nullable=False)
    tamano = db.Column(db.String(50), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    carpeta_id = db.Column(db.Integer, db.ForeignKey('carpeta.id'), nullable=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)

    # Por ahora hardcodeamos el usuario (para compatibilidad)
    usuario_nombre = db.Column(db.String(100), default="Admin User")
    usuario_avatar = db.Column(db.String(255), default="account_circle")
    usuario_email = db.Column(db.String(255), default="admin@nuvoryx.com")

    def __repr__(self):
        return f'<Archivo {self.nombre_original}>'
