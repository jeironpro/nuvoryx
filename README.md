# Nuvoryx 🌥️

[![Pre-commit](https://github.com/jeironpro/nuvoryx/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/jeironpro/nuvoryx/actions/workflows/pre-commit.yml)
[![Lint](https://github.com/jeironpro/nuvoryx/actions/workflows/lint.yml/badge.svg)](https://github.com/jeironpro/nuvoryx/actions/workflows/lint.yml)
[![Tests](https://github.com/jeironpro/nuvoryx/actions/workflows/test.yml/badge.svg)](https://github.com/jeironpro/nuvoryx/actions/workflows/test.yml)

## 📌 Descripción

Este proyecto forma parte de mi portafolio personal.
El objetivo es demostrar buenas prácticas de programación, organización y documentación en GitHub.

**Nuvoryx** es un sistema de gestión de archivos en la nube con las siguientes características:

- 🔐 Autenticación de usuarios (registro, login, logout)
- 📁 Gestión de carpetas y archivos
- 🔍 Búsqueda y filtrado de archivos
- 📊 Estadísticas de uso
- 🎨 Interfaz moderna con glassmorphism y **Modo Oscuro**
- 🔒 Relaciones de base de datos con integridad referencial
- 🏗️ Arquitectura modular con Blueprints y Application Factory

## 🚀 Tecnologías

### Backend

- **Flask** - Framework web (Blueprints structure)
- **SQLAlchemy** - ORM
- **MySQL** - Base de datos
- **Flask-Login** - Gestión de sesiones
- **bcrypt** - Hash de contraseñas

### Frontend

- **HTML5** / **CSS3** (modular, variables CSS, dark mode support)
- **JavaScript** (ES6 Modules)
- **Material Symbols** - Iconografía

## 📦 Instalación

### Requisitos

- Python 3.9+
- MySQL 8.0+
- Node.js (para validación de JS - opcional)

### Configuración

1. **Clonar el repositorio**

```bash
git clone https://github.com/jeironpro/nuvoryx.git
cd nuvoryx
```

2. **Crear entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -e .
```

4. **Configurar base de datos**

```bash
mysql -u root -p
CREATE DATABASE nuvoryx;
```

Crea un archivo `.env` basado en el ejemplo o configura las variables de entorno necesarias (`DATABASE_URL`, `SECRET_KEY`, etc.).

5. **Ejecutar aplicación**

```bash
python app.py
```

La aplicación estará disponible en `http://127.0.0.1:5555`

## 🛠️ Desarrollo

### Estructura del Proyecto Refactorizada

```
nuvoryx/
├── app.py                 # Punto de entrada (Application Factory)
├── blueprints/            # Módulos de la aplicación
│   ├── auth.py           # Rutas de autenticación
│   ├── files.py          # Rutas de gestión de archivos
│   └── main.py           # Rutas principales
├── config.py              # Configuraciones (Dev, Test, Prod)
├── extensions.py          # Inicialización de extensiones (db, mail, login)
├── models.py              # Modelos de base de datos
├── static/                # Assets (CSS modificado para Dark Mode)
├── templates/             # Plantillas Jinja2 (Base template restructure)
└── tests/                 # Tests actualizados
```

### Ejecutar Tests

```bash
pytest -v
```

## 📜 Licencia

Este proyecto está bajo la licencia **MIT**.
Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**jeironpro**
