# Makefile for Segmind Python Client

.PHONY: help install install-dev test test-verbose test-coverage test-html clean lint check build build-check publish-test clean-dist

# Default target
help:
	@echo "Available targets:"
	@echo "  install       - Install production dependencies"
	@echo "  install-dev   - Install development dependencies"
	@echo "  test          - Run tests"
	@echo "  test-verbose  - Run tests with verbose output"
	@echo "  test-coverage - Run tests with coverage report"
	@echo "  test-html     - Generate HTML coverage report"
	@echo "  clean         - Clean up generated files"
	@echo "  lint          - Run linting checks"
	@echo "  check         - Run all checks (lint + test)"
	@echo "  build         - Build distribution packages"
	@echo "  build-check   - Build and validate packages"
	@echo "  publish-test  - Publish to TestPyPI (requires TestPyPI token)"
	@echo "  clean-dist    - Clean distribution files"

# Install production dependencies
install:
	pip install -e .

# Install development dependencies
install-dev:
	pip install -e ".[dev,test]"

# Run tests
test:
	python -m pytest tests/ -v

# Run tests with verbose output
test-verbose:
	python -m pytest tests/ -v -s --tb=long

# Run tests with coverage
test-coverage:
	python -m pytest tests/ -v --cov=segmind --cov-report=term-missing

# Generate HTML coverage report
test-html:
	python -m pytest tests/ -v --cov=segmind --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# Clean up generated files
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Run linting checks
lint:
	pre-commit run --all-files

# Run all checks
check: lint test-coverage

# Build distribution packages
build:
	pip install --upgrade build
	python -m build

# Build and validate packages
build-check:
	pip install --upgrade build twine
	rm -rf dist/
	python -m build
	twine check dist/*
	@echo "Build successful! Packages validated."

# Publish to TestPyPI (for testing before production release)
publish-test: build-check
	@echo "Publishing to TestPyPI..."
	@echo "Make sure TEST_PYPI_API_TOKEN environment variable is set"
	twine upload --repository testpypi dist/* --verbose

# Clean distribution files
clean-dist:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
