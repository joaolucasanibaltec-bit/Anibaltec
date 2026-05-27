#!/bin/bash

# Script para compilar o conversor para Linux
# Execute este script em uma máquina Linux

echo "Instalando dependências..."
pip install -r requirements.txt
pip install pyinstaller

echo "Compilando executável..."
pyinstaller --onefile --name ConversorACSN_SgaCloud conversor_acsn_sgacloud.py

echo "Compilação concluída!"
echo "Executável disponível em: dist/ConversorACSN_SgaCloud"
echo "Não esqueça de incluir o arquivo ibge_municipios.csv na distribuição"