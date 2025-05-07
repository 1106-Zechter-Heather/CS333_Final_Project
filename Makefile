.PHONY: test coverage lint type-check format clean build install dev-install

# Default target
all: lint type-check test

# Run all tests
test:
	pytest

# Run tests with coverage
coverage:
	pytest --cov=src tests/
	coverage report
	coverage html

# Run linting
lint:
	flake8 src tests
	black --check src tests
	isort --check-only --profile black src tests

# Run type checking
type-check:
	mypy src

# Format code
format:
	black src tests
	isort --profile black src tests

# Build the package
build: clean
	python -m build --sdist --wheel

# Install the package
install:
	pip install -e .

# Install development dependencies
dev-install:
	pip install -r dev-requirements.txt
	pip install -e .

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Release-related tasks
release-test:
	twine check dist/*

release-upload:
	twine upload dist/*

# Help message
help:
	@echo "Available targets:"
	@echo "  make test          Run all tests"
	@echo "  make coverage      Run tests with coverage report"
	@echo "  make lint          Run linting"
	@echo "  make type-check    Run type checking"
	@echo "  make format        Format code with black and isort"
	@echo "  make build         Build the package"
	@echo "  make clean         Clean up build artifacts"
	@echo "  make install       Install the package"
	@echo "  make dev-install   Install development dependencies"
	@echo "  make release-test  Check the package for PyPI release"
	@echo "  make release-upload Upload the package to PyPI"