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
        assert http_client.headers["User-Agent"] == "segmind-python/0.1.0"

    def test_http_client_headers_without_api_key(self):
        """Test HTTP client headers when no API key is provided."""
        client = SegmindClient()
        http_client = client._build_client()

        assert "x-api-key" not in http_client.headers
        assert http_client.headers["User-Agent"] == "segmind-python/0.1.0"

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


class TestClientAdvancedFeatures:
    """Test cases for advanced client features and edge cases."""

    def test_base_url_trailing_slash_handling(self, mock_api_key):
        """Test that trailing slashes are properly handled in base_url."""
        urls_to_test = [
            "https://api.segmind.com/v1",
            "https://api.segmind.com/v1/",
            "https://api.segmind.com/v1//",
        ]
        
        for url in urls_to_test:
            client = SegmindClient(api_key=mock_api_key, base_url=url)
            assert client.base_url == "https://api.segmind.com/v1"

    def test_client_timeout_edge_cases(self, mock_api_key):
        """Test client timeout with edge case values."""
        timeout_values = [0.1, 1.0, 30.0, 60.0, 300.0]
        
        for timeout in timeout_values:
            client = SegmindClient(api_key=mock_api_key, timeout=timeout)
            assert client.timeout == timeout
            
            http_client = client._build_client()
            assert http_client.timeout.read == timeout

    def test_client_initialization_with_custom_user_agent(self, mock_api_key):
        """Test that User-Agent header is correctly set."""
        client = SegmindClient(api_key=mock_api_key)
        http_client = client._build_client()
        
        assert "User-Agent" in http_client.headers
        assert http_client.headers["User-Agent"] == "segmind-python/0.1.0"

    def test_client_initialization_with_all_parameters(self, mock_api_key):
        """Test client initialization with all parameters specified."""
        client = SegmindClient(
            api_key=mock_api_key,
            base_url="https://custom.api.com/v2",
            timeout=45.0
        )
        
        assert client.api_key == mock_api_key
        assert client.base_url == "https://custom.api.com/v2"
        assert client.timeout == 45.0

    def test_run_method_with_empty_parameters(self, mock_api_key):
        """Test run method with no additional parameters."""
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            response = client.run("test-model")

            assert response.status_code == 200
            mock_client.post.assert_called_once_with("/test-model", json={})

    def test_run_method_with_complex_parameters(self, mock_api_key):
        """Test run method with complex nested parameters."""
        complex_params = {
            "prompt": "Generate an image",
            "settings": {
                "quality": "high",
                "style": {"type": "photorealistic", "intensity": 0.8},
                "dimensions": {"width": 1024, "height": 768}
            },
            "metadata": {
                "tags": ["test", "image", "ai"],
                "created_by": "test_user"
            },
            "options": [{"name": "option1", "value": True}, {"name": "option2", "value": 42}]
        }

        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            response = client.run("complex-model", **complex_params)

            assert response.status_code == 200
            mock_client.post.assert_called_once_with("/complex-model", json=complex_params)

    def test_run_method_with_special_model_names(self, mock_api_key):
        """Test run method with various model name formats."""
        model_names = [
            "simple-model",
            "model_with_underscores",
            "model.with.dots",
            "model123",
            "MODEL-UPPERCASE",
            "model-v1.2.3",
            "namespace/model-name"
        ]

        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)

            for model_name in model_names:
                response = client.run(model_name, prompt="test")
                assert response.status_code == 200

    def test_request_method_with_query_parameters(self, mock_api_key):
        """Test _request method with query parameters."""
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            response = client._request(
                "GET", 
                "test-endpoint", 
                params={"page": 1, "limit": 10, "filter": "active"}
            )

            assert response.status_code == 200
            mock_client.request.assert_called_once_with(
                "GET", 
                "test-endpoint", 
                params={"page": 1, "limit": 10, "filter": "active"}
            )

    def test_request_method_with_headers(self, mock_api_key):
        """Test _request method with additional headers."""
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "test"}
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            additional_headers = {"X-Custom-Header": "value", "X-Request-ID": "12345"}
            
            response = client._request(
                "POST", 
                "test-endpoint", 
                headers=additional_headers,
                json={"test": "data"}
            )

            assert response.status_code == 200
            mock_client.request.assert_called_once_with(
                "POST", 
                "test-endpoint", 
                headers=additional_headers,
                json={"test": "data"}
            )

    def test_request_method_with_files(self, mock_api_key):
        """Test _request method with file upload."""
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"uploaded": True}
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            files_data = {"file": ("test.txt", b"test content", "text/plain")}
            
            response = client._request("POST", "upload-endpoint", files=files_data)

            assert response.status_code == 200
            mock_client.request.assert_called_once_with(
                "POST", 
                "upload-endpoint", 
                files=files_data
            )

    def test_http_client_connect_timeout(self, mock_api_key):
        """Test that connect timeout is properly configured."""
        client = SegmindClient(api_key=mock_api_key, timeout=30.0)
        http_client = client._build_client()
        
        assert http_client.timeout.connect == 5.0  # Default connect timeout
        assert http_client.timeout.read == 30.0

    def test_service_properties_type_consistency(self, mock_api_key):
        """Test that service properties return correct types consistently."""
        client = SegmindClient(api_key=mock_api_key)
        
        # Test multiple accesses return same instance type
        models1 = client.models
        models2 = client.models
        assert type(models1) == type(models2)
        
        generations1 = client.generations
        generations2 = client.generations
        assert type(generations1) == type(generations2)

    def test_client_with_none_values(self, mock_api_key):
        """Test client initialization with None values."""
        client = SegmindClient(api_key=mock_api_key, base_url=None, timeout=None)
        
        # Should use defaults when None is passed
        assert client.api_key == mock_api_key
        assert client.base_url == "https://api.segmind.com/v1"
        assert client.timeout == 30.0

    def test_error_propagation_in_run_method(self, mock_api_key):
        """Test that various errors are properly propagated in run method."""
        import httpx
        
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            
            # Test network error
            mock_client.post.side_effect = httpx.NetworkError("Connection failed")
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            
            with pytest.raises(httpx.NetworkError):
                client.run("test-model", prompt="test")

    def test_error_propagation_in_request_method(self, mock_api_key):
        """Test that various errors are properly propagated in _request method."""
        import httpx
        
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            
            # Test timeout error
            mock_client.request.side_effect = httpx.TimeoutException("Request timed out")
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            
            with pytest.raises(httpx.TimeoutException):
                client._request("GET", "test-endpoint")

    @pytest.mark.parametrize("method", ["GET", "POST", "PUT", "DELETE", "PATCH"])
    def test_request_method_with_various_http_methods(self, mock_api_key, method):
        """Test _request method with various HTTP methods."""
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"method": method}
            mock_client.request.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            response = client._request(method, "test-endpoint")

            assert response.status_code == 200
            mock_client.request.assert_called_once_with(method, "test-endpoint")

    def test_client_recreates_http_client_on_build(self, mock_api_key):
        """Test that _build_client creates a new client instance each time."""
        client = SegmindClient(api_key=mock_api_key)
        
        http_client1 = client._build_client()
        http_client2 = client._build_client()
        
        # Should be different instances
        assert http_client1 is not http_client2
        # But with same configuration
        assert http_client1.headers == http_client2.headers

    def test_run_method_url_construction(self, mock_api_key):
        """Test that run method constructs URLs correctly."""
        with mock.patch("segmind.client.httpx.Client") as mock_client_class:
            mock_client = mock.MagicMock()
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "success"}
            mock_client.post.return_value = mock_response
            mock_client_class.return_value = mock_client

            client = SegmindClient(api_key=mock_api_key)
            
            # Test various model slug formats
            test_cases = [
                ("simple-model", "/simple-model"),
                ("namespace/model", "/namespace/model"),
                ("model-v1.2.3", "/model-v1.2.3"),
            ]
            
            for model_slug, expected_url in test_cases:
                client.run(model_slug, prompt="test")
                call_args = mock_client.post.call_args
                assert call_args[0][0] == expected_url

    def test_stream_method_current_implementation(self, mock_api_key):
        """Test current implementation of stream method."""
        client = SegmindClient(api_key=mock_api_key)
        
        # Current implementation returns None
        result = client.stream("test-model", prompt="test", stream=True)
        assert result is None
        
        # Test with various parameters
        result = client.stream(
            "complex-model", 
            prompt="test", 
            max_tokens=100, 
            temperature=0.7
        )
        assert result is None

    def test_client_state_isolation(self, mock_api_key):
        """Test that multiple client instances are properly isolated."""
        client1 = SegmindClient(api_key="key1", base_url="https://api1.com")
        client2 = SegmindClient(api_key="key2", base_url="https://api2.com")
        
        assert client1.api_key != client2.api_key
        assert client1.base_url != client2.base_url
        assert client1._client is not client2._client

    def test_service_namespace_independence(self, mock_api_key):
        """Test that service namespaces are independent between clients."""
        client1 = SegmindClient(api_key=mock_api_key)
        client2 = SegmindClient(api_key=mock_api_key)
        
        # Services should be different instances
        assert client1.models is not client2.models
        assert client1.generations is not client2.generations
        assert client1.files is not client2.files
        
        # But should reference their respective clients
        assert client1.models._client is client1
        assert client2.models._client is client2
