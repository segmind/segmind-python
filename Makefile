# Makefile for Segmind Python Client

.PHONY: help install install-dev test test-verbose test-coverage test-html clean lint check

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
