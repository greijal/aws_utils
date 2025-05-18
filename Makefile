PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PIP := $(BIN)/pip

.PHONY: all
all: clean setup install test

.PHONY: setup
setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

.PHONY: install
install:
	$(PIP) install -r requirements.txt

.PHONY: install-dev
install-dev: install
	$(PIP) install -e ".[dev]"

.PHONY: test
test:
	$(BIN)/pytest tests/ -v

.PHONY: coverage
coverage:
	$(BIN)/pytest --cov=src/aws_utils tests/

.PHONY: clean
clean:
	rm -rf $(VENV)
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf __pycache__
	rm -rf .pytest_cache
	rm -rf .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: docker-up
docker-up:
	docker-compose up -d

.PHONY: docker-down
docker-down:
	docker-compose down

.PHONY: run
run:
	$(BIN)/python cli.py

.PHONY: black
black:
	$(BIN)/black src/ tests/

.PHONY: type
type:
	$(BIN)/mypy src/

.PHONY: check
check:
	$(BIN)/flake8 src/ tests/

.PHONY: isort
isort:
	$(BIN)/isort src/ tests/

.PHONY: format
format:black isort type
	$(BIN)/flake8 src/ tests/



.PHONY: help
help:
	@echo "Comandos disponíveis:"
	@echo "  make setup         - Criar ambiente virtual"
	@echo "  make install      - Instalar dependências"
	@echo "  make install-dev  - Instalar dependências de desenvolvimento"
	@echo "  make test         - Executar testes"
	@echo "  make coverage     - Executar testes com cobertura"
	@echo "  make clean        - Limpar arquivos temporários"
	@echo "  make docker-up    - Iniciar containers Docker"
	@echo "  make docker-down  - Parar containers Docker"
	@echo "  make run          - Executar CLI"
	@echo "  make format       - Formatar código com black"
	@echo "  make type         - Verificar tipos com mypy"
	@echo "  make lint         - Verificar código com flake8"