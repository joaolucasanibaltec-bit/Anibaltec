#!/usr/bin/env bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

echo "============================================"
echo " SGA -> SGAcloud - Conversor Desktop"
echo "============================================"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "ERRO: Python 3 nao encontrado."
    exit 1
fi

PYTHON=$(command -v python3)

if [ ! -d ".venv" ]; then
    echo "[setup] Criando ambiente virtual..."
    $PYTHON -m venv .venv
fi

source .venv/bin/activate

if [ ! -f ".venv/.deps_ok" ]; then
    echo "[setup] Instalando dependencias..."
    pip install -q -r requirements.txt
    touch .venv/.deps_ok
fi

echo "Iniciando aplicacao desktop..."
echo ""

exec $PYTHON app.py
