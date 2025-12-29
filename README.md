# 🚀 Nuvoryx

<div align="center">

![Nuvoryx Logo](static/icon/nuvoryx.png)

[![Pre-commit](https://github.com/jeironpro/nuvoryx/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/jeironpro/nuvoryx/actions/workflows/pre-commit.yml)
[![Lint](https://github.com/jeironpro/nuvoryx/actions/workflows/lint.yml/badge.svg)](https://github.com/jeironpro/nuvoryx/actions/workflows/lint.yml)
[![Tests](https://github.com/jeironpro/nuvoryx/actions/workflows/test.yml/badge.svg)](https://github.com/jeironpro/nuvoryx/actions/workflows/test.yml)

**Sistema moderno de gestión de archivos en la nube**

Este proyecto se creo utilizando los modelos de Antigravity. Yo solo fui quien pedia funcionalidades de manera técnica y el modelo las agregaba, luego yo verificaba y probaba que todo funcionaba correctamente.

Me enfoque en pedir muchas de las cosas que estoy aprendiendo en la empresa que hago las prácticas de desarrollo de aplicaciones web.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Características](#-características) • [Instalación](#-instalación) • [Uso](#-uso) • [Tecnologías](#-tecnologías)

</div>

---

### 📁 Gestión Completa de Archivos

- **Subida de carpetas recursiva**: Arrastra directorios completos manteniendo su estructura.
- **Organización jerárquica**: Carpetas infinitas y archivos vinculados.
- **Búsqueda y filtrado**: Localización inmediata de elementos.
- **Acciones masivas**: Descarga masiva en ZIP y eliminación conjunta.
- **Diseño Premium**: Interfaz basada en tarjetas con glassmorphism.

---

## 📖 Documentación

Para una comprensión más profunda del sistema, consulta nuestro [Manual Técnico](docs/MANUAL_TECNICO.md) (también disponible en la carpeta de documentos del proyecto).

### 👁️ Visualización Universal

Nuvoryx puede previsualizar **todos** los tipos de archivo:

#### Soportados Nativamente

- **Documentos**: PDF, Word (.docx con mammoth.js)
- **Imágenes**: JPG, PNG, GIF, SVG, WebP
- **Video**: MP4, WebM, OGG, AVI
- **Audio**: MP3, WAV, OGG, M4A
- **Código**: JavaScript, Python, HTML, CSS, JSON, XML, YAML, SQL
- **Datos**: CSV, JSON, Markdown
- **Texto**: TXT, LOG, README

#### Fallback Inteligente

Para archivos no soportados nativamente (Excel, PowerPoint, archivos comprimidos, etc.):

- **Icono grande** del tipo de archivo
- **Metadata útil**: Extensión, tamaño, tipo
- **Descripción** del formato
- **Botón de descarga** prominente

### 📱 Responsive Espectacular

#### Mobile (< 640px)

- **Vista de tarjetas**: Cada archivo es una tarjeta vertical
- **Información esencial**: Nombre, tamaño, fecha
- **Checkbox grande**: Fácil de tocar (44x44px)
- **Acciones touch-friendly**: Botones grandes y espaciados

#### Tablet (640px - 1024px)

- **Tabla compacta**: Oculta columnas menos importantes
- **Iconos grandes**: Optimizados para touch
- **Espaciado generoso**: Evita clicks accidentales

#### Desktop (>= 1024px)

- **Tabla completa**: Todas las columnas visibles
- **Hover states**: Feedback visual rico
- **Acciones inline**: Siempre visibles

### 🔐 Autenticación Segura

- **Registro de usuarios** con validación de contraseñas
- **Inicio de sesión** seguro
- **Recuperación de contraseña** por email
- **Gestión de perfil**: Cambiar email, contraseña, eliminar cuenta

### 🎨 UI Moderna

- **Modales premium**: Diseño limpio con iconos centrados
- **Botones uniformes**: Mismo tamaño en todos los modales
- **Animaciones suaves**: Transiciones fluidas
- **Auto-focus**: Cursor automático en inputs
- **Enter to submit**: Enviar formularios con Enter

---

## 🛠️ Tecnologías

### Backend

- **Flask 3.0+**: Framework web Python
- **SQLAlchemy**: ORM para base de datos
- **Flask-Login**: Gestión de sesiones
- **Flask-Mail**: Envío de emails
- **Werkzeug**: Seguridad y utilidades

### Frontend

- **Vanilla JavaScript (ES6 Modules)**: Sin frameworks pesados
- **CSS Moderno**: Variables, Grid, Flexbox
- **Material Symbols**: Iconos de Google
- **Librerías**:
  - `mammoth.js`: Preview de Word (.docx)
  - `marked.js`: Renderizado de Markdown
  - `highlight.js`: Syntax highlighting de código

### Base de Datos

- **SQLite**: Base de datos ligera y portable

---

## 📦 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Git

### Pasos

1. **Clonar el repositorio**

```bash
git clone https://github.com/tuusuario/nuvoryx.git
cd nuvoryx
```

2. **Crear entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
y/o
pip install -r test-requirements.txt
```

4. **Configurar variables de entorno**
   Crea un archivo `.env` en la raíz del proyecto:

```env
SECRET_KEY=tu-clave-secreta-muy-segura
DATABASE_URL="motor_de_base_de_datos+libreria_de_conexion://usuario:contraseña@direccion_de_la_base_de_datos/nombre_de_la_base_de_datos"
TRACK_MODIFICATIONS=False
UPLOAD_FOLDER="uploads"
SECURITY_PASSWORD_SALT="tu-clave-secreta-muy-segura"
MAX_CONTENT_LENGTH=524288000
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=tu-email@gmail.com
MAIL_PASSWORD=tu-contraseña-de-aplicación
```

5. **Inicializar la base de datos**

```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

6. **Ejecutar la aplicación**

```bash
python app.py
```

7. **Abrir en el navegador**

```
http://localhost:5000
```

---

## 🎯 Uso

### Subir Archivos

1. Arrastra archivos a la zona de subida o haz click para seleccionar
2. Los archivos se suben automáticamente
3. Verás una notificación de éxito

### Crear Carpetas

1. Click en "Nueva Carpeta"
2. Ingresa el nombre
3. Presiona Enter o click en "Crear"

### Previsualizar Archivos

1. Click en cualquier archivo de la tabla
2. Se abrirá el modal de previsualización
3. Usa el botón de descarga si necesitas el archivo original

### Acciones Masivas

1. Selecciona múltiples archivos con los checkboxes
2. Aparecerá la barra de acciones masivas
3. Elimina o descarga todos a la vez (ZIP)

### Cambiar Vista

- Click en el icono de vista (lista/cuadrícula) en la barra superior
- La preferencia se guarda automáticamente

---

## 📂 Estructura del Proyecto

```
nuvoryx/
├── app.py                      # Aplicación principal Flask
├── config.py                   # Configuración
├── requirements.txt            # Dependencias Python
├── .env                        # Variables de entorno (no incluido)
│
├── blueprints/                 # Módulos de la aplicación
│   ├── autenticacion.py       # Login, registro, recuperación
│   └── archivos.py            # Gestión de archivos y carpetas
│
├── models/                     # Modelos de base de datos
│   ├── usuario.py             # Modelo de Usuario
│   └── archivo.py             # Modelo de Archivo
│
├── utils/                      # Utilidades
│   ├── correo.py              # Envío de emails
│   └── utilidades.py          # Funciones auxiliares
│
├── static/                     # Archivos estáticos
│   ├── css/                   # Estilos
│   │   ├── base/              # Variables, globales
│   │   ├── components/        # Componentes (modales, tabla, etc.)
│   │   └── layout/            # Layouts (contenedores, navegación)
│   ├── js/                    # JavaScript
│   │   └── modules/           # Módulos ES6
│   └── icon/                  # Iconos y logo
│
├── templates/                  # Templates Jinja2
│   ├── base.html              # Template base
│   ├── index.html             # Página principal
│   └── partials/              # Componentes reutilizables
│
└── uploads/                    # Archivos subidos (gitignored)
```

---

## 🎨 Capturas de Pantalla

### Desktop

![Vista Desktop](docs/screenshots/desktop.png)

### Preview de Archivos

![Preview](docs/screenshots/preview.png)

---

## 🔒 Seguridad

- **Contraseñas hasheadas**: Usando Werkzeug
- **Validación de archivos**: Tipos y tamaños permitidos
- **CSRF Protection**: Tokens en formularios
- **SQL Injection**: Protegido por SQLAlchemy ORM
- **XSS Prevention**: Escapado de HTML en templates

---

## 🚀 Roadmap

- [ ] Compartir archivos con otros usuarios
- [ ] Permisos y roles (admin, usuario, invitado)
- [ ] Integración con almacenamiento en la nube (S3, Google Drive)
- [ ] Búsqueda avanzada con filtros
- [ ] Etiquetas y categorías
- [ ] Versioning de archivos
- [ ] API REST completa
- [ ] App móvil nativa

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

---

## 👨‍💻 Autores

**Modelos de Antigravity y jeironpro**

- GitHub: [@jeironpro](https://github.com/jeironpro)
- Email: jeironprogrammer@gmail.com

---

## 🙏 Agradecimientos

- [Flask](https://flask.palletsprojects.com) - Framework web
- [Material Symbols](https://fonts.google.com/icons) - Iconos
- [Mammoth.js](https://github.com/mwilliamson/mammoth.js) - Preview de Word
- [Marked.js](https://marked.js.org) - Markdown parser
- [Highlight.js](https://highlightjs.org) - Syntax highlighting

---

<div align="center">

**⭐ Si te gusta este proyecto, dale una estrella en GitHub! ⭐**

</div>
