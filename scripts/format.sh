#!/bin/bash

echo "🎨 Formateando código con Black..."
black .

echo "📦 Ordenando imports con isort..."
isort .

echo "✅ Formateo completado!"
