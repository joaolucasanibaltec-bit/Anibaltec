@echo off
title SGA -> SGAcloud Converter (Desktop)
cd /d "%~dp0"
echo ============================================
echo  SGA -> SGAcloud - Conversor Desktop
echo ============================================
echo.
echo Iniciando aplicacao...
echo.
python app.py
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Python nao encontrado ou dependencias faltando.
    echo Execute: pip install -r requirements.txt
    pause
)
