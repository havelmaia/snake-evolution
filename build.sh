#!/bin/bash
set -e

echo "=== Snake Evolution - Build ==="

# Instalar PyInstaller se necessário
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "Instalando PyInstaller..."
    pip install pyinstaller
fi

# Limpar builds anteriores
rm -rf build/ dist/

# Build
echo "Gerando executável..."
pyinstaller snake.spec

echo ""
echo "=== Build concluído! ==="
echo "Executável em: dist/SnakeEvolution"
echo "Rode com: ./dist/SnakeEvolution"
