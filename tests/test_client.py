"""Tests for the SegmindClient class."""

from unittest import mock

import pytest

from segmind.client import SegmindClient
from segmind.exceptions import SegmindError


class TestSegmindClient:
    """Test cases for the SegmindClient class."""

    def test_client_initialization_with_api_key(self, mock_api_key, mock_base_url, mock_timeout):
        """Test client initialization with explicit API key."""
        client = SegmindClient(api_key=mock_api_key, base_url=mock_base_url, timeout=mock_timeout)

        assert client.api_key == mock_api_key
        assert client.base_url == mock_base_url
        assert client.timeout == mock_timeout

    def test_client_initialization_without_api_key(
        self, mock_environment, mock_base_url, mock_timeout
    ):
        """Test client initialization without explicit API key (uses environment)."""
        client = SegmindClient(base_url=mock_base_url, timeout=mock_timeout)

        assert client.api_key == "env-api-key-67890"
        assert client.base_url == mock_base_url
        assert client.timeout == mock_timeout

    def test_http_client_headers(self, mock_api_key):
        """Test HTTP client header configuration."""
        client = SegmindClient(api_key=mock_api_key)
        http_client = client._build_client()

        assert http_client.headers["x-api-key"] == mock_api_key
        assert http_client.headers["User-Agent"] == "segmind-python-sdk/0.1.0"
        assert http_client.headers["X-Initiator"] == "segmind-python-sdk/0.1.0"


    def test_http_client_headers_without_api_key(self):
        """Test HTTP client headers when no API key is provided."""
        client = SegmindClient()
        http_client = client._build_client()

        assert "x-api-key" not in http_client.headers
        assert http_client.headers["User-Agent"] == "segmind-python-sdk/0.1.0"
        assert http_client.headers["X-Initiator"] == "segmind-python-sdk/0.1.0"


    def test_http_client_timeout_configuration(self, mock_api_key):
        """Test HTTP client timeout configuration."""
        client = SegmindClient(api_key=mock_api_key, timeout=5.0)
        http_client = client._build_client()

        assert http_client.timeout.read == 5.0
        assert http_client.timeout.connect == 5.0

    def test_run_method_success(self, mock_api_key, sample_generation_data):
        """Test successful model run request."""
        # Mock the internal httpx client
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = sample_generation_data
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            response = client.run("test-model", prompt="Hello world")

            assert response.status_code == 200
            assert response.json() == sample_generation_data
            mock_client.post.assert_called_once_with("/test-model", json={"prompt": "Hello world"})

    def test_run_method_with_parameters(self, mock_api_key):
        """Test model run with various parameters."""
        # Mock the internal httpx client
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            params = {"prompt": "Hello world", "max_tokens": 100, "temperature": 0.7}
            response = client.run("test-model", **params)

            assert response.status_code == 200
            mock_client.post.assert_called_once_with("/test-model", json=params)

    def test_run_method_error_handling(self, mock_api_key):
        """Test error handling in run method."""
        # Mock the internal httpx client to return an error response
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 400
            mock_response.json.return_value = {
                "error": "Bad Request",
                "detail": "Invalid parameters",
            }
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)

            with pytest.raises(SegmindError) as exc_info:
                client.run("test-model", prompt="test")

            assert "400" in str(exc_info.value)

    def test_stream_method_not_implemented(self, mock_api_key):
        """Test that stream method is not implemented."""
        client = SegmindClient(api_key=mock_api_key)

        # Currently returns None (not implemented)
        result = client.stream("test-model", prompt="test")
        assert result is None

    def test_request_method_get(self, mock_api_key):
        """Test _request method with GET request."""
        # Mock the internal httpx client
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            response = client._request("GET", "test-endpoint")

            assert response.status_code == 200
            assert response.json() == {"data": "test"}
            mock_client.request.assert_called_once_with("GET", "test-endpoint")

    def test_request_method_post(self, mock_api_key):
        """Test _request method with POST request."""
        # Mock the internal httpx client
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "created"}
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            response = client._request("POST", "test-endpoint", json={"key": "value"})

            assert response.status_code == 200
            assert response.json() == {"status": "created"}
            mock_client.request.assert_called_once_with(
                "POST", "test-endpoint", json={"key": "value"}
            )

    def test_request_method_error_handling(self, mock_api_key):
        """Test error handling in _request method."""
        # Mock the internal httpx client to return an error response
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {"error": "Internal Server Error"}
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)

            with pytest.raises(SegmindError) as exc_info:
                client._request("GET", "test-endpoint")

            assert "500" in str(exc_info.value)

    def test_service_attributes(self, mock_api_key):
        """Test that service attributes are properly initialized."""
        client = SegmindClient(api_key=mock_api_key)

        # Check that all service attributes exist
        assert hasattr(client, "models")
        assert hasattr(client, "generations")
        assert hasattr(client, "files")
        assert hasattr(client, "pixelflows")
        assert hasattr(client, "webhooks")
        assert hasattr(client, "accounts")

    def test_service_client_reference(self, mock_api_key):
        """Test that service instances have correct client reference."""
        client = SegmindClient(api_key=mock_api_key)

        # Check that services reference the correct client
        assert client.models._client == client
        assert client.generations._client == client
        assert client.files._client == client
        assert client.pixelflows._client == client
        assert client.webhooks._client == client
        assert client.accounts._client == client


class TestClientEnvironmentHandling:
    """Test cases for environment variable handling."""

    def test_api_key_from_environment_after_import(self, mock_environment):
        """Test that API key is read from environment after import."""
        client = SegmindClient()
        assert client.api_key == "env-api-key-67890"

    def test_api_key_parameter_overrides_environment(self, mock_environment, mock_api_key):
        """Test that explicit API key parameter overrides environment variable."""
        client = SegmindClient(api_key=mock_api_key)
        assert client.api_key == mock_api_key

    def test_no_api_key_handling(self):
        """Test behavior when no API key is provided."""
        client = SegmindClient()
        assert client.api_key is None
