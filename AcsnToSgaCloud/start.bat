@echo off
title AcsnToSgaCloud - Conversor ACSN para SGAcloud

echo ============================================
echo  AcsnToSgaCloud - Conversor ACSN para SGAcloud
echo ============================================
echo.

:: Verifica se o executavel existe e executa direto
if exist "%~dp0AcsnToSgaCloud.exe" (
    echo Iniciando versao standalone...
    start "" "%~dp0AcsnToSgaCloud.exe"
    goto :fim
)

:: Verifica se Python esta instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Erro: Python nao encontrado.
    echo Instale Python 3.8+ em https://python.org
    pause
    exit /b 1
)

:: Verifica e instala dependencias
echo Verificando dependencias...
pip install -r "%~dp0backend\requirements.txt" -q 2>nul

:: Inicia o servidor
echo.
echo Iniciando servidor em http://localhost:20000
echo.
start http://localhost:20000
python "%~dp0run.py"

:fim
pause
