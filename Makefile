.PHONY: install dev test lint format type-check security-audit check clean

PYTHON := python3
VENV := .venv
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python

install:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	$(VENV)/bin/pre-commit install
	@echo "Setup complete. Activate with: source $(VENV)/bin/activate"

dev:
	$(PIP) install -r requirements-dev.txt

test:
	$(PYTHON_VENV) -m pytest

lint:
	$(PYTHON_VENV) -m ruff check skills/claude-youtube/execution

format:
	$(PYTHON_VENV) -m ruff format skills/claude-youtube/execution

type-check:
	$(PYTHON_VENV) -m mypy skills/claude-youtube/execution

security-audit:
	$(PYTHON_VENV) -m bandit -r skills/claude-youtube/execution
	$(PYTHON_VENV) -m pip_audit

check: lint type-check test

clean:
	rm -rf $(VENV) .pytest_cache .coverage .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
