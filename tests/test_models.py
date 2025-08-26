"""Tests for the Models service class."""

from unittest import mock

import pytest

from segmind.models import Models


class TestModels:
    """Test cases for the Models service class."""

    def test_models_initialization(self):
        """Test Models service initialization."""
        mock_client = mock.MagicMock()
        models = Models(mock_client)

        assert models._client == mock_client
        assert isinstance(models, Models)

    def test_models_list_success(self):
        """Test successful models listing."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "models": [{"id": "model-1", "name": "Model 1"}, {"id": "model-2", "name": "Model 2"}]
        }
        mock_client._request.return_value = mock_response

        models = Models(mock_client)
        result = models.list()

        assert "models" in result
        assert len(result["models"]) == 2
        assert result["models"][0]["id"] == "model-1"
        assert result["models"][1]["name"] == "Model 2"

    def test_models_list_calls_correct_endpoint(self):
        """Test that models.list() calls the correct endpoint."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"models": []}
        mock_client._request.return_value = mock_response

        models = Models(mock_client)
        models.list()

        mock_client._request.assert_called_once_with(
            "GET", "https://api.spotprod.segmind.com/inference-model-information/list"
        )

    def test_models_list_error_handling(self):
        """Test error handling in models.list()."""
        mock_client = mock.MagicMock()
        mock_client._request.side_effect = Exception("API Error")

        models = Models(mock_client)

        with pytest.raises(Exception) as exc_info:
            models.list()

        assert "API Error" in str(exc_info.value)

    def test_models_inheritance(self):
        """Test that Models inherits from Namespace."""
        from segmind.resource import Namespace

        mock_client = mock.MagicMock()
        models = Models(mock_client)

        assert isinstance(models, Namespace)
        assert models._client == mock_client

    def test_models_methods_exist(self):
        """Test that all expected methods exist on Models service."""
        mock_client = mock.MagicMock()
        models = Models(mock_client)

        assert hasattr(models, "list")
        assert callable(models.list)

    def test_models_list_response_structure(self):
        """Test that models.list() response has expected structure."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "models": [
                {
                    "id": "test-model",
                    "name": "Test Model",
                    "description": "A test model",
                    "version": "1.0.0",
                }
            ],
            "total": 1,
            "page": 1,
        }
        mock_client._request.return_value = mock_response

        models = Models(mock_client)
        result = models.list()

        # Check response structure
        assert "models" in result
        assert "total" in result
        assert "page" in result
        assert isinstance(result["models"], list)
        assert isinstance(result["total"], int)
        assert isinstance(result["page"], int)

        # Check model structure
        model = result["models"][0]
        assert "id" in model
        assert "name" in model
        assert "description" in model
        assert "version" in model
