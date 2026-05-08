@echo off
title SGA -> SGAcloud - Servidor Web
cd /d "%~dp0"
echo ============================================
echo  SGA -> SGAcloud - Servidor Web
echo ============================================
echo.
echo Iniciando servidor API em http://localhost:8000
echo Interface web em http://localhost:8000/frontend/
echo Pressione CTRL+C para parar
echo.
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
if %errorlevel% neq 0 (
    echo.
    echo ERRO: Python nao encontrado ou dependencias faltando.
    echo Execute: pip install -r requirements.txt
    pause
)
