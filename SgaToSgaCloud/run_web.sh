#!/usr/bin/env bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$APP_DIR"

echo "============================================"
echo " SGA -> SGAcloud - Servidor Web"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERRO: Python 3 nao encontrado. Instale python3 e pip."
    exit 1
fi

PYTHON=$(command -v python3)

# Auto-create venv if missing
if [ ! -d ".venv" ]; then
    echo "[setup] Criando ambiente virtual..."
    $PYTHON -m venv .venv
fi

# Activate venv
source .venv/bin/activate

# Auto-install deps if missing
if [ ! -f ".venv/.deps_ok" ]; then
    echo "[setup] Instalando dependencias..."
    pip install -q -r requirements.txt
    touch .venv/.deps_ok
    echo "[setup] Concluido."
fi

echo "Iniciando servidor em http://localhost:8000"
echo "Acessar de outros computadores: http://$(hostname -I 2>/dev/null | awk '{print $1}'):8000"
echo "Pressione CTRL+C para parar"
echo ""

exec $PYTHON -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
