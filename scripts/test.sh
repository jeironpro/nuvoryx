#!/bin/bash

echo "🧪 Ejecutando tests con pytest..."

pytest -v --cov --cov-report=term-missing --cov-report=html

echo ""
echo "✅ Tests completados!"
echo "📊 Reporte de cobertura generado en htmlcov/index.html"
