#!/bin/bash
# Script para formatear código con black e isort

echo "🎨 Formateando código con Black..."
black .

echo "📦 Ordenando imports con isort..."
isort .

echo "✅ Formateo completado!"
