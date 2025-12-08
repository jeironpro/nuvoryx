#!/bin/bash
# Script para ejecutar linters

echo "🔍 Ejecutando linters..."

echo ""
echo "1️⃣ Verificando formato con Black..."
black --check . || exit 1

echo ""
echo "2️⃣ Ejecutando Flake8..."
flake8 . || exit 1

echo ""
echo "3️⃣ Verificando imports con isort..."
isort --check-only . || exit 1

echo ""
echo "✅ Todos los linters pasaron correctamente!"
