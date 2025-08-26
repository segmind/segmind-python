"""Shared fixtures and configuration for Segmind client tests."""

import pytest


@pytest.fixture
def mock_api_key():
    """Mock API key for testing."""
    return "test-api-key-12345"


@pytest.fixture
def mock_base_url():
    """Mock base URL for testing."""
    return "https://api.segmind.com/v1"


@pytest.fixture
def mock_timeout():
    """Mock timeout value for testing."""
    return 30.0


@pytest.fixture
def mock_environment(monkeypatch):
    """Set up mock environment variables."""
    monkeypatch.setenv("SEGMIND_API_KEY", "env-api-key-67890")
    return {"SEGMIND_API_KEY": "env-api-key-67890"}


@pytest.fixture
def sample_generation_data():
    """Sample generation data for testing."""
    return {
        "id": "gen-123",
        "model": "test-model-123",
        "status": "completed",
        "output": "Generated content here",
        "created_at": "2024-01-01T00:00:00Z",
    }
