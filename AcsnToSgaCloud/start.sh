#!/bin/bash
# AcsnToSgaCloud - Conversor ACSN para SGAcloud

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================"
echo " AcsnToSgaCloud - Conversor ACSN para SGAcloud"
echo "============================================"
echo ""

# Verifica se o executavel existe
if [ -f "./AcsnToSgaCloud" ]; then
    echo "Iniciando versao standalone..."
    ./AcsnToSgaCloud &
    sleep 2
    xdg-open "http://localhost:20000" 2>/dev/null || true
    wait
    exit 0
fi

# Verifica se Python esta instalado
if ! command -v python3 &>/dev/null; then
    echo "Erro: Python3 nao encontrado."
    echo "Instale Python 3.8+ com: sudo apt install python3 python3-pip"
    exit 1
fi

# Verifica e instala dependencias
echo "Verificando dependencias..."
pip3 install -r "$SCRIPT_DIR/backend/requirements.txt" -q 2>/dev/null

# Inicia o servidor
echo ""
echo "Iniciando servidor em http://localhost:20000"
echo ""
xdg-open "http://localhost:20000" 2>/dev/null || true
python3 "$SCRIPT_DIR/run.py"
