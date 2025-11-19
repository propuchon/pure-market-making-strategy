.PHONY: help install pip-compile pip-sync clean test run setup lint format

help:
	@echo "Available commands:"
	@echo "  make setup        - Install pip-tools and setup project"
	@echo "  make pip-compile  - Compile requirements.in to requirements.txt"
	@echo "  make pip-sync     - Sync environment with requirements.txt"
	@echo "  make install      - Install all dependencies"
	@echo "  make run          - Run the market maker bot"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter (ruff)"
	@echo "  make format       - Format code (ruff)"
	@echo "  make clean        - Remove cache files"

setup:
	pip install --upgrade pip
	pip install pip-tools
	$(MAKE) pip-compile
	$(MAKE) pip-sync

pip-compile:
	pip-compile requirements.in --output-file=requirements.txt --resolver=backtracking

pip-sync:
	pip-sync requirements.txt

install:
	pip install -r requirements.txt

run:
	python main.py

test:
	pytest tests/ -v

lint:
	ruff check .

format:
	ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

