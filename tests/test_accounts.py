"""Comprehensive tests for the Accounts module."""

from unittest import mock

import pytest
import httpx

from segmind.accounts import Accounts


class TestAccounts:
    """Test cases for the Accounts class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = mock.MagicMock()
        client._request = mock.MagicMock()
        return client

    @pytest.fixture
    def accounts(self, mock_client):
        """Create an Accounts instance with mock client."""
        acc = Accounts(client=mock_client)
        acc._client = mock_client
        return acc

    @pytest.fixture
    def sample_account_data(self):
        """Sample account data for testing."""
        return {
            "user_id": "user_12345",
            "email": "test@example.com",
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "subscription": {
                "plan": "pro",
                "status": "active",
                "expires_at": "2024-12-31T23:59:59Z"
            },
            "credits": {
                "balance": 1000,
                "used": 250,
                "total": 1250
            },
            "api_key_info": {
                "key_id": "key_123",
                "created_at": "2024-01-01T00:00:00Z",
                "last_used": "2024-01-15T12:30:00Z"
            },
            "account_created": "2023-12-01T00:00:00Z",
            "last_login": "2024-01-15T08:00:00Z",
            "timezone": "UTC",
            "preferences": {
                "notifications": True,
                "newsletter": False
            }
        }

    @pytest.fixture
    def sample_free_account_data(self):
        """Sample free account data for testing."""
        return {
            "user_id": "user_67890",
            "email": "free@example.com",
            "username": "freeuser",
            "first_name": "Free",
            "last_name": "User",
            "subscription": {
                "plan": "free",
                "status": "active",
                "expires_at": None
            },
            "credits": {
                "balance": 100,
                "used": 50,
                "total": 150
            },
            "account_created": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-15T10:00:00Z"
        }

    # ==================== Test current() method ====================

    def test_current_account_success(self, accounts, mock_client, sample_account_data):
        """Test successful retrieval of current account information."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_account_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result == sample_account_data
        assert result["user_id"] == "user_12345"
        assert result["email"] == "test@example.com"
        assert result["subscription"]["plan"] == "pro"
        assert result["credits"]["balance"] == 1000
        
        mock_client._request.assert_called_once_with(
            "GET",
            "https://cloud.segmind.com/api/auth/authenticate"
        )

    def test_current_account_free_plan(self, accounts, mock_client, sample_free_account_data):
        """Test retrieval of free account information."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_free_account_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result["subscription"]["plan"] == "free"
        assert result["subscription"]["expires_at"] is None
        assert result["credits"]["balance"] == 100
        mock_client._request.assert_called_once()

    def test_current_account_minimal_data(self, accounts, mock_client):
        """Test current() with minimal account data."""
        minimal_data = {
            "user_id": "user_min",
            "email": "minimal@example.com",
            "subscription": {"plan": "basic", "status": "active"}
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = minimal_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result["user_id"] == "user_min"
        assert result["email"] == "minimal@example.com"
        assert result["subscription"]["plan"] == "basic"

    def test_current_account_network_error(self, accounts, mock_client):
        """Test current() when network error occurs."""
        mock_client._request.side_effect = httpx.NetworkError("Connection failed")

        with pytest.raises(httpx.NetworkError):
            accounts.current()

    def test_current_account_timeout_error(self, accounts, mock_client):
        """Test current() when request times out."""
        mock_client._request.side_effect = httpx.TimeoutException("Request timed out")

        with pytest.raises(httpx.TimeoutException):
            accounts.current()

    def test_current_account_authentication_error(self, accounts, mock_client):
        """Test current() with authentication error."""
        mock_client._request.side_effect = httpx.HTTPStatusError(
            "Unauthorized",
            request=mock.MagicMock(),
            response=mock.MagicMock(status_code=401)
        )

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            accounts.current()
        
        assert exc_info.value.response.status_code == 401

    def test_current_account_forbidden_error(self, accounts, mock_client):
        """Test current() with forbidden error."""
        mock_client._request.side_effect = httpx.HTTPStatusError(
            "Forbidden",
            request=mock.MagicMock(),
            response=mock.MagicMock(status_code=403)
        )

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            accounts.current()
        
        assert exc_info.value.response.status_code == 403

    def test_current_account_server_error(self, accounts, mock_client):
        """Test current() with server error."""
        mock_client._request.side_effect = httpx.HTTPStatusError(
            "Internal Server Error",
            request=mock.MagicMock(),
            response=mock.MagicMock(status_code=500)
        )

        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            accounts.current()
        
        assert exc_info.value.response.status_code == 500

    def test_current_account_json_parsing_error(self, accounts, mock_client):
        """Test current() when response JSON is invalid."""
        mock_response = mock.MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client._request.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON"):
            accounts.current()

    def test_current_account_empty_response(self, accounts, mock_client):
        """Test current() with empty response."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {}
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result == {}
        mock_client._request.assert_called_once()

    # ==================== Test URL and API endpoint ====================

    def test_current_account_correct_url(self, accounts, mock_client, sample_account_data):
        """Test that current() uses the correct API endpoint."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_account_data
        mock_client._request.return_value = mock_response

        accounts.current()

        mock_client._request.assert_called_once_with(
            "GET",
            "https://cloud.segmind.com/api/auth/authenticate"
        )

    def test_current_account_request_method(self, accounts, mock_client, sample_account_data):
        """Test that current() uses GET method."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_account_data
        mock_client._request.return_value = mock_response

        accounts.current()

        # Verify GET method was used
        call_args = mock_client._request.call_args
        assert call_args[0][0] == "GET"

    def test_current_account_no_additional_parameters(self, accounts, mock_client, sample_account_data):
        """Test that current() doesn't send additional parameters."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_account_data
        mock_client._request.return_value = mock_response

        accounts.current()

        # Verify only method and URL were passed, no json, params, etc.
        call_args = mock_client._request.call_args
        assert len(call_args[0]) == 2  # method and url
        assert len(call_args[1]) == 0  # no keyword arguments

    # ==================== Test different account states ====================

    def test_current_account_suspended(self, accounts, mock_client):
        """Test current() with suspended account."""
        suspended_data = {
            "user_id": "user_suspended",
            "email": "suspended@example.com",
            "subscription": {
                "plan": "pro",
                "status": "suspended"
            },
            "credits": {"balance": 0}
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = suspended_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result["subscription"]["status"] == "suspended"
        assert result["credits"]["balance"] == 0

    def test_current_account_expired_subscription(self, accounts, mock_client):
        """Test current() with expired subscription."""
        expired_data = {
            "user_id": "user_expired",
            "email": "expired@example.com",
            "subscription": {
                "plan": "pro",
                "status": "expired",
                "expires_at": "2023-12-31T23:59:59Z"
            }
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = expired_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result["subscription"]["status"] == "expired"
        assert "2023-12-31" in result["subscription"]["expires_at"]

    def test_current_account_trial_period(self, accounts, mock_client):
        """Test current() with trial account."""
        trial_data = {
            "user_id": "user_trial",
            "email": "trial@example.com",
            "subscription": {
                "plan": "trial",
                "status": "active",
                "trial_ends_at": "2024-02-01T00:00:00Z"
            },
            "credits": {"balance": 500, "trial_credits": True}
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = trial_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result["subscription"]["plan"] == "trial"
        assert result["credits"]["trial_credits"] is True

    # ==================== Test response data validation ====================

    def test_current_account_with_nested_data(self, accounts, mock_client):
        """Test current() with deeply nested account data."""
        nested_data = {
            "user_id": "user_nested",
            "profile": {
                "personal": {
                    "name": {"first": "John", "last": "Doe"},
                    "contact": {
                        "email": "john.doe@example.com",
                        "phone": "+1-555-0123"
                    }
                },
                "professional": {
                    "company": "Example Corp",
                    "role": "Developer"
                }
            },
            "settings": {
                "api": {
                    "rate_limits": {"requests_per_minute": 60},
                    "allowed_endpoints": ["inference", "pixelflows"]
                },
                "billing": {
                    "auto_recharge": True,
                    "recharge_amount": 100
                }
            }
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = nested_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result["profile"]["personal"]["name"]["first"] == "John"
        assert result["settings"]["api"]["rate_limits"]["requests_per_minute"] == 60
        assert result["settings"]["billing"]["auto_recharge"] is True

    def test_current_account_with_special_characters(self, accounts, mock_client):
        """Test current() with special characters in account data."""
        special_data = {
            "user_id": "user_special",
            "email": "test+user@example.com",
            "first_name": "José",
            "last_name": "Müller",
            "company": "Acme Corp & Associates",
            "bio": "Software engineer with 10+ years experience in AI/ML 🤖"
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = special_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result["email"] == "test+user@example.com"
        assert result["first_name"] == "José"
        assert result["last_name"] == "Müller"
        assert "🤖" in result["bio"]

    def test_current_account_with_null_values(self, accounts, mock_client):
        """Test current() with null values in response."""
        null_data = {
            "user_id": "user_nulls",
            "email": "user@example.com",
            "first_name": None,
            "last_name": None,
            "company": None,
            "phone": None,
            "subscription": {
                "plan": "free",
                "expires_at": None
            }
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = null_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result["first_name"] is None
        assert result["last_name"] is None
        assert result["subscription"]["expires_at"] is None

    # ==================== Performance and reliability tests ====================

    def test_current_account_multiple_calls(self, accounts, mock_client, sample_account_data):
        """Test multiple consecutive calls to current()."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_account_data
        mock_client._request.return_value = mock_response

        # Make multiple calls
        results = []
        for _ in range(5):
            result = accounts.current()
            results.append(result)

        # Verify all calls succeeded and returned same data
        for result in results:
            assert result == sample_account_data
            assert result["user_id"] == "user_12345"

        assert mock_client._request.call_count == 5

    def test_current_account_response_size_handling(self, accounts, mock_client):
        """Test current() with large response data."""
        # Create a large response to test memory handling
        large_data = {
            "user_id": "user_large",
            "email": "large@example.com",
            "large_field": "x" * 10000,  # 10KB string
            "array_data": list(range(1000)),  # Large array
            "nested_large": {
                "data": ["item_" + str(i) for i in range(500)]
            }
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = large_data
        mock_client._request.return_value = mock_response

        result = accounts.current()

        assert result["user_id"] == "user_large"
        assert len(result["large_field"]) == 10000
        assert len(result["array_data"]) == 1000
        assert len(result["nested_large"]["data"]) == 500

    @pytest.mark.parametrize("status_code,expected_exception", [
        (400, httpx.HTTPStatusError),
        (401, httpx.HTTPStatusError),
        (403, httpx.HTTPStatusError),
        (404, httpx.HTTPStatusError),
        (429, httpx.HTTPStatusError),
        (500, httpx.HTTPStatusError),
        (502, httpx.HTTPStatusError),
        (503, httpx.HTTPStatusError),
    ])
    def test_current_account_various_http_errors(self, accounts, mock_client, status_code, expected_exception):
        """Test current() with various HTTP error codes."""
        mock_client._request.side_effect = httpx.HTTPStatusError(
            f"HTTP {status_code}",
            request=mock.MagicMock(),
            response=mock.MagicMock(status_code=status_code)
        )

        with pytest.raises(expected_exception) as exc_info:
            accounts.current()
        
        assert exc_info.value.response.status_code == status_code