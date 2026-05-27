.PHONY: setup run-web run-desktop clean

APP_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

help:
	@echo "SGA -> SGAcloud"
	@echo ""
	@echo "Uso: make <target>"
	@echo ""
	@echo "Targets:"
	@echo "  setup        Cria virtualenv e instala dependencias"
	@echo "  run-web      Inicia servidor web (http://localhost:8000)"
	@echo "  run-desktop  Inicia aplicacao desktop (CustomTkinter)"
	@echo "  clean        Remove virtualenv e caches"

setup:
	@echo "[setup] Criando virtualenv..."
	python3 -m venv .venv
	@echo "[setup] Instalando dependencias..."
	.venv/bin/pip install -r requirements.txt
	@touch .venv/.deps_ok
	@echo "[setup] Concluido."

run-web: setup
	@.venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

run-desktop: setup
	@.venv/bin/python3 app.py

clean:
	@rm -rf .venv __pycache__ */__pycache__ */*/__pycache__
	@rm -f .venv/.deps_ok
	@echo "[clean] Concluido."
