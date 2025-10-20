# MAXX Ecosystem Makefile
# Convenient commands for development, testing, and deployment

.PHONY: help install install-dev test test-unit test-integration test-performance lint format type-check security clean run docker-build docker-run docs

# Default target
help:
	@echo "MAXX Ecosystem - Available Commands:"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  clean        Clean up temporary files"
	@echo ""
	@echo "Testing:"
	@echo "  test         Run all tests"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint         Run linting checks"
	@echo "  format       Format code with black and isort"
	@echo "  type-check   Run type checking with mypy"
	@echo "  security     Run security checks with bandit"
	@echo ""
	@echo "Development:"
	@echo "  run          Run the application"
	@echo "  dev          Run in development mode"
	@echo "  docs         Generate documentation"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run Docker container"
	@echo ""

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -e .

# Cleaning
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# Testing
test:
	pytest

test-unit:
	pytest -m unit

test-integration:
	pytest -m integration

test-performance:
	pytest -m performance -v

test-cov:
	pytest --cov=. --cov-report=html --cov-report=term-missing

test-watch:
	pytest-watch -- -v

# Code Quality
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black .
	isort .

format-check:
	black --check .
	isort --check-only .

type-check:
	mypy . --ignore-missing-imports

security:
	bandit -r . -f json -o bandit-report.json
	safety check

# Development
run:
	python main.py

dev:
	python main.py --log-level DEBUG

docs:
	@echo "Generating documentation..."
	@mkdir -p docs
	@echo "# API Documentation" > docs/api.md
	@echo "Generated API documentation would go here" >> docs/api.md

# Docker
docker-build:
	docker build -t maxx-ecosystem .

docker-run:
	docker run -p 8000:8000 --env-file .env maxx-ecosystem

# Development workflow
check: format-check lint type-check security test

ci: install-dev check test-cov

# Release
build: clean
	python setup.py sdist bdist_wheel

# Database management
db-init:
	@echo "Initializing database..."
	python -c "import asyncio; from main import MAXXEcosystem; asyncio.run(MAXXEcosystem().initialize())"

db-migrate:
	@echo "Running database migrations..."
	@echo "Migration logic would go here"

db-backup:
	@echo "Creating database backup..."
	@mkdir -p backups
	@cp data/ecosystem.db backups/ecosystem_$(shell date +%Y%m%d_%H%M%S).db

# Performance monitoring
profile:
	python -m cProfile -o profile.stats main.py
	python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"

benchmark:
	pytest --benchmark-only

# Utilities
install-pre-commit:
	pre-commit install

update-deps:
	pip-compile requirements.in
	pip-compile requirements-dev.in

check-deps:
	pip-audit

# Environment setup
setup-env:
	@if [ ! -f .env ]; then \
		echo "Creating .env file from template..."; \
		cp .env.example .env; \
		echo "Please edit .env with your configuration"; \
	fi

setup-dirs:
	@mkdir -p data logs backups reports

# Full setup
setup: setup-env setup-dirs install-dev install-pre-commit
	@echo "Setup complete! Please edit .env with your configuration."

# Quick start
quickstart: setup
	@echo "Quick start complete!"
	@echo "Run 'make run' to start the application"
	@echo "Run 'make test' to run tests"
	@echo "Run 'make dev' for development mode"