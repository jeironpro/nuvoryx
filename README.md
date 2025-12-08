# Nuvoryx 🌥️

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
- 🎨 Interfaz moderna con glassmorphism
- 🔒 Relaciones de base de datos con integridad referencial

## 🚀 Tecnologías

### Backend

- **Flask** - Framework web
- **SQLAlchemy** - ORM
- **MySQL** - Base de datos
- **Flask-Login** - Gestión de sesiones
- **bcrypt** - Hash de contraseñas

### Frontend

- **HTML5** / **CSS3** (modular)
- **JavaScript** (ES6 Modules)
- **Material Symbols** - Iconografía

## 📦 Instalación

### Requisitos

- Python 3.9+
- MySQL 8.0+
- Node.js (para validación de JS)

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

5. **Ejecutar aplicación**

```bash
python app.py
```

La aplicación estará disponible en `http://127.0.0.1:5005`

## 🛠️ Desarrollo

### Instalar dependencias de desarrollo

```bash
pip install -e ".[dev]"
```

### Formatear código

```bash
./scripts/format.sh
# O manualmente:
black .
isort .
```

### Ejecutar linters

```bash
./scripts/lint.sh
# O manualmente:
black --check .
flake8 .
isort --check-only .
```

### Estructura del Proyecto

```
nuvoryx/
├── app.py                 # Aplicación principal
├── models.py              # Modelos de base de datos
├── static/
│   ├── css/
│   │   ├── main.css      # Punto de entrada CSS
│   │   ├── base/         # Variables, reset
│   │   ├── components/   # Componentes UI
│   │   └── layout/       # Layouts
│   └── js/
│       ├── main.js       # Punto de entrada JS
│       └── modules/      # Módulos ES6
├── templates/
│   ├── index.html        # Template principal
│   └── partials/         # Componentes HTML
├── tests/                # Tests con pytest
│   ├── conftest.py       # Fixtures
│   ├── test_models.py    # Tests de modelos
│   ├── test_auth.py      # Tests de autenticación
│   ├── test_files.py     # Tests de archivos
│   └── test_routes.py    # Tests de rutas
└── uploads/              # Archivos subidos
```

## 🧪 Testing

### Ejecutar tests

```bash
./scripts/test.sh
# O manualmente:
pytest -v
```

### Tests con cobertura

```bash
pytest --cov --cov-report=html
# Ver reporte: htmlcov/index.html
```

### Tests específicos

```bash
# Solo tests de modelos
pytest tests/test_models.py

# Solo tests de autenticación
pytest tests/test_auth.py

# Test específico
pytest tests/test_auth.py::test_login_exitoso
```

### Estructura de Tests

- **test_models.py** - Tests de modelos (Usuario, Carpeta, Archivo)
- **test_auth.py** - Tests de autenticación (registro, login, logout)
- **test_files.py** - Tests de operaciones con archivos/carpetas
- **test_routes.py** - Tests de rutas y navegación

## 📜 Licencia

Este proyecto está bajo la licencia **MIT**.  
Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 👤 Autor

**jeironpro**
