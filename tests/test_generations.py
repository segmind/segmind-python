"""Tests for the Generations service class."""

from unittest import mock

import pytest

from segmind.generations import Generations


class TestGenerations:
    """Test cases for the Generations service class."""

    def test_generations_initialization(self):
        """Test Generations service initialization."""
        mock_client = mock.MagicMock()
        generations = Generations(mock_client)

        assert generations._client == mock_client
        assert isinstance(generations, Generations)

    def test_generations_list_success(self):
        """Test successful generations listing."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "generations": [
                {"id": "gen-1", "status": "completed"},
                {"id": "gen-2", "status": "processing"},
            ]
        }
        mock_client._request.return_value = mock_response

        generations = Generations(mock_client)
        result = generations.list()

        assert "generations" in result
        assert len(result["generations"]) == 2
        assert result["generations"][0]["id"] == "gen-1"
        assert result["generations"][1]["status"] == "processing"

    def test_generations_list_calls_correct_endpoint(self):
        """Test that generations.list() calls the correct endpoint."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"generations": []}
        mock_client._request.return_value = mock_response

        generations = Generations(mock_client)
        generations.list()

        mock_client._request.assert_called_once_with(
            "GET",
            "https://api.spotprod.segmind.com/inference-request/generations",
            params={"page": 1},
        )

    def test_generations_list_with_parameters(self):
        """Test generations listing with query parameters."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"generations": []}
        mock_client._request.return_value = mock_response

        generations = Generations(mock_client)
        generations.list(page=2, model_name="test-model", start_date="2024-01-01")

        mock_client._request.assert_called_once_with(
            "GET",
            "https://api.spotprod.segmind.com/inference-request/generations",
            params={"page": 2, "model_name": "test-model", "start_date": "2024-01-01"},
        )

    def test_generations_recent_success(self):
        """Test successful recent generations retrieval."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "generations": [{"id": "gen-123", "status": "completed", "model": "test-model"}]
        }
        mock_client._request.return_value = mock_response

        generations = Generations(mock_client)
        result = generations.recent("test-model")

        assert "generations" in result
        assert len(result["generations"]) == 1
        assert result["generations"][0]["id"] == "gen-123"
        assert result["generations"][0]["status"] == "completed"

    def test_generations_recent_requires_model_name(self):
        """Test that generations.recent() requires model_name parameter."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"generations": []}
        mock_client._request.return_value = mock_response

        generations = Generations(mock_client)
        generations.recent("test-model")

        mock_client._request.assert_called_once_with(
            "GET",
            "https://api.spotprod.segmind.com/inference-request/recent-generations",
            params={"model_name": "test-model"},
        )

    def test_generations_error_handling(self):
        """Test error handling in generations methods."""
        mock_client = mock.MagicMock()
        mock_client._request.side_effect = Exception("API Error")

        generations = Generations(mock_client)

        with pytest.raises(Exception) as exc_info:
            generations.list()

        assert "API Error" in str(exc_info.value)

    def test_generations_inheritance(self):
        """Test that Generations inherits from Namespace."""
        from segmind.resource import Namespace

        mock_client = mock.MagicMock()
        generations = Generations(mock_client)

        assert isinstance(generations, Namespace)
        assert generations._client == mock_client

    def test_generations_methods_exist(self):
        """Test that all expected methods exist on Generations service."""
        mock_client = mock.MagicMock()
        generations = Generations(mock_client)

        assert hasattr(generations, "list")
        assert hasattr(generations, "recent")
        assert callable(generations.list)
        assert callable(generations.recent)

    def test_generations_response_structure(self):
        """Test that generations responses have expected structure."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "generations": [
                {
                    "id": "test-gen",
                    "status": "completed",
                    "model": "test-model",
                    "created_at": "2024-01-01T00:00:00Z",
                    "output": "Generated text",
                }
            ],
            "total": 1,
            "page": 1,
        }
        mock_client._request.return_value = mock_response

        generations = Generations(mock_client)
        result = generations.list()

        # Check response structure
        assert "generations" in result
        assert "total" in result
        assert "page" in result
        assert isinstance(result["generations"], list)
        assert isinstance(result["total"], int)
        assert isinstance(result["page"], int)

        # Check generation structure
        generation = result["generations"][0]
        assert "id" in generation
        assert "status" in generation
        assert "model" in generation
        assert "created_at" in generation
        assert "output" in generation

    def test_generations_list_default_page_parameter(self):
        """Test that generations.list() uses default page parameter."""
        mock_client = mock.MagicMock()
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"generations": []}
        mock_client._request.return_value = mock_response

        generations = Generations(mock_client)
        generations.list()  # No page parameter specified

        # Should use default page=1
        mock_client._request.assert_called_once_with(
            "GET",
            "https://api.spotprod.segmind.com/inference-request/generations",
            params={"page": 1},
        )
