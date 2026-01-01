"""Comprehensive tests for the Webhooks module."""

from unittest import mock

import pytest
import httpx

from segmind.webhooks import Webhooks


class TestWebhooks:
    """Test cases for the Webhooks class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = mock.MagicMock()
        client._request = mock.MagicMock()
        return client

    @pytest.fixture
    def webhooks(self, mock_client):
        """Create a Webhooks instance with mock client."""
        wh = Webhooks(client=mock_client)
        wh._client = mock_client
        return wh

    @pytest.fixture
    def sample_webhook_data(self):
        """Sample webhook data for testing."""
        return {
            "webhook_id": "wh-123456",
            "webhook_url": "https://example.com/webhook",
            "event_types": ["PIXELFLOW"],
            "status": "active",
            "created_at": "2024-01-01T00:00:00Z"
        }

    @pytest.fixture
    def sample_webhooks_list(self):
        """Sample list of webhooks for testing."""
        return {
            "webhooks": [
                {
                    "webhook_id": "wh-123",
                    "webhook_url": "https://example1.com/webhook",
                    "event_types": ["PIXELFLOW"],
                    "status": "active"
                },
                {
                    "webhook_id": "wh-456",
                    "webhook_url": "https://example2.com/webhook",
                    "event_types": ["PIXELFLOW", "GENERATION"],
                    "status": "inactive"
                }
            ]
        }

    # ==================== Test get() method ====================

    def test_get_webhooks_success(self, webhooks, mock_client, sample_webhooks_list):
        """Test successful retrieval of all webhooks."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_webhooks_list
        mock_client._request.return_value = mock_response

        result = webhooks.get()

        assert result == sample_webhooks_list
        assert len(result["webhooks"]) == 2
        mock_client._request.assert_called_once_with(
            "GET", 
            "https://api.spotprod.segmind.com/webhook/get"
        )

    def test_get_webhooks_empty_list(self, webhooks, mock_client):
        """Test get() when no webhooks exist."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"webhooks": []}
        mock_client._request.return_value = mock_response

        result = webhooks.get()

        assert result["webhooks"] == []
        mock_client._request.assert_called_once()

    def test_get_webhooks_network_error(self, webhooks, mock_client):
        """Test get() when network error occurs."""
        mock_client._request.side_effect = httpx.NetworkError("Connection failed")

        with pytest.raises(httpx.NetworkError):
            webhooks.get()

    # ==================== Test add() method ====================

    def test_add_webhook_success(self, webhooks, mock_client, sample_webhook_data):
        """Test successful webhook addition."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "webhook_id": "wh-123456",
            "message": "Webhook added successfully"
        }
        mock_client._request.return_value = mock_response

        result = webhooks.add(
            webhook_url="https://example.com/webhook",
            event_types=["PIXELFLOW"]
        )

        assert result["status"] == "success"
        assert result["webhook_id"] == "wh-123456"
        mock_client._request.assert_called_once_with(
            "POST",
            "https://api.spotprod.segmind.com/webhook/add",
            json={
                "webhook_url": "https://example.com/webhook",
                "event": {"types": ["PIXELFLOW"]}
            }
        )

    def test_add_webhook_multiple_event_types(self, webhooks, mock_client):
        """Test adding webhook with multiple event types."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"status": "success", "webhook_id": "wh-multi"}
        mock_client._request.return_value = mock_response

        result = webhooks.add(
            webhook_url="https://example.com/multi-webhook",
            event_types=["PIXELFLOW", "GENERATION", "MODEL_INFERENCE"]
        )

        assert result["status"] == "success"
        mock_client._request.assert_called_once_with(
            "POST",
            "https://api.spotprod.segmind.com/webhook/add",
            json={
                "webhook_url": "https://example.com/multi-webhook",
                "event": {"types": ["PIXELFLOW", "GENERATION", "MODEL_INFERENCE"]}
            }
        )

    def test_add_webhook_empty_event_types_raises_error(self, webhooks):
        """Test that add() raises ValueError with empty event types."""
        with pytest.raises(ValueError, match="Event types must be specified"):
            webhooks.add(
                webhook_url="https://example.com/webhook",
                event_types=[]
            )

    def test_add_webhook_none_event_types_raises_error(self, webhooks):
        """Test that add() raises ValueError with None event types."""
        with pytest.raises(ValueError, match="Event types must be specified"):
            webhooks.add(
                webhook_url="https://example.com/webhook",
                event_types=None
            )

    def test_add_webhook_with_https_url(self, webhooks, mock_client):
        """Test adding webhook with HTTPS URL."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"status": "success", "webhook_id": "wh-https"}
        mock_client._request.return_value = mock_response

        webhooks.add(
            webhook_url="https://secure.example.com/webhook/endpoint",
            event_types=["PIXELFLOW"]
        )

        mock_client._request.assert_called_once()
        call_args = mock_client._request.call_args
        assert call_args[1]["json"]["webhook_url"] == "https://secure.example.com/webhook/endpoint"

    def test_add_webhook_with_query_params(self, webhooks, mock_client):
        """Test adding webhook with URL containing query parameters."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"status": "success", "webhook_id": "wh-query"}
        mock_client._request.return_value = mock_response

        webhook_url = "https://example.com/webhook?token=abc123&version=v1"
        webhooks.add(webhook_url=webhook_url, event_types=["PIXELFLOW"])

        call_args = mock_client._request.call_args
        assert call_args[1]["json"]["webhook_url"] == webhook_url

    # ==================== Test update() method ====================

    def test_update_webhook_success(self, webhooks, mock_client):
        """Test successful webhook update."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "webhook_id": "wh-123456",
            "message": "Webhook updated successfully"
        }
        mock_client._request.return_value = mock_response

        result = webhooks.update(
            webhook_id="wh-123456",
            webhook_url="https://updated.example.com/webhook",
            event_types=["PIXELFLOW", "GENERATION"]
        )

        assert result["status"] == "success"
        assert result["webhook_id"] == "wh-123456"
        mock_client._request.assert_called_once_with(
            "POST",
            "https://api.spotprod.segmind.com/webhook/update",
            json={
                "webhook_id": "wh-123456",
                "webhook_url": "https://updated.example.com/webhook",
                "event": {"types": ["PIXELFLOW", "GENERATION"]}
            }
        )

    def test_update_webhook_single_event_type(self, webhooks, mock_client):
        """Test updating webhook with single event type."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_client._request.return_value = mock_response

        webhooks.update(
            webhook_id="wh-single",
            webhook_url="https://single.example.com/webhook",
            event_types=["PIXELFLOW"]
        )

        call_args = mock_client._request.call_args
        assert call_args[1]["json"]["event"]["types"] == ["PIXELFLOW"]

    def test_update_webhook_empty_event_types_raises_error(self, webhooks):
        """Test that update() raises ValueError with empty event types."""
        with pytest.raises(ValueError, match="Event types must be specified"):
            webhooks.update(
                webhook_id="wh-123",
                webhook_url="https://example.com/webhook",
                event_types=[]
            )

    def test_update_webhook_none_event_types_raises_error(self, webhooks):
        """Test that update() raises ValueError with None event types."""
        with pytest.raises(ValueError, match="Event types must be specified"):
            webhooks.update(
                webhook_id="wh-123",
                webhook_url="https://example.com/webhook",
                event_types=None
            )

    def test_update_webhook_different_url(self, webhooks, mock_client):
        """Test updating webhook with completely different URL."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_client._request.return_value = mock_response

        webhooks.update(
            webhook_id="wh-change-url",
            webhook_url="https://completely-different.com/new/endpoint",
            event_types=["GENERATION", "MODEL_INFERENCE"]
        )

        call_args = mock_client._request.call_args
        assert call_args[1]["json"]["webhook_url"] == "https://completely-different.com/new/endpoint"
        assert "GENERATION" in call_args[1]["json"]["event"]["types"]
        assert "MODEL_INFERENCE" in call_args[1]["json"]["event"]["types"]

    # ==================== Test delete() method ====================

    def test_delete_webhook_success(self, webhooks, mock_client):
        """Test successful webhook deletion."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "webhook_id": "wh-123456",
            "message": "Webhook marked as inactive"
        }
        mock_client._request.return_value = mock_response

        result = webhooks.delete("wh-123456")

        assert result["status"] == "success"
        assert result["webhook_id"] == "wh-123456"
        mock_client._request.assert_called_once_with(
            "GET",
            "https://api.spotprod.segmind.com/webhook/inactive",
            params={"webhook_id": "wh-123456"}
        )

    def test_delete_webhook_with_special_characters(self, webhooks, mock_client):
        """Test deleting webhook with special characters in ID."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"status": "success"}
        mock_client._request.return_value = mock_response

        webhooks.delete("wh-123_special-chars.456")

        mock_client._request.assert_called_once_with(
            "GET",
            "https://api.spotprod.segmind.com/webhook/inactive",
            params={"webhook_id": "wh-123_special-chars.456"}
        )

    def test_delete_nonexistent_webhook(self, webhooks, mock_client):
        """Test deleting a non-existent webhook."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "status": "error",
            "message": "Webhook not found"
        }
        mock_client._request.return_value = mock_response

        result = webhooks.delete("wh-nonexistent")

        assert result["status"] == "error"
        assert result["message"] == "Webhook not found"

    # ==================== Test logs() method ====================

    def test_logs_webhook_success(self, webhooks, mock_client):
        """Test successful retrieval of webhook logs."""
        sample_logs = {
            "webhook_id": "wh-123456",
            "logs": [
                {
                    "timestamp": "2024-01-01T10:00:00Z",
                    "event_type": "PIXELFLOW",
                    "status": "delivered",
                    "response_code": 200,
                    "response_time_ms": 150
                },
                {
                    "timestamp": "2024-01-01T09:30:00Z",
                    "event_type": "PIXELFLOW",
                    "status": "failed",
                    "response_code": 404,
                    "response_time_ms": 5000,
                    "error": "Not Found"
                }
            ]
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_logs
        mock_client._request.return_value = mock_response

        result = webhooks.logs("wh-123456")

        assert result["webhook_id"] == "wh-123456"
        assert len(result["logs"]) == 2
        assert result["logs"][0]["status"] == "delivered"
        assert result["logs"][1]["status"] == "failed"
        mock_client._request.assert_called_once_with(
            "GET",
            "https://api.spotprod.segmind.com/webhook/dispatch-logs",
            params={"webhook_id": "wh-123456"}
        )

    def test_logs_webhook_empty_logs(self, webhooks, mock_client):
        """Test logs() when no logs exist for webhook."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "webhook_id": "wh-no-logs",
            "logs": []
        }
        mock_client._request.return_value = mock_response

        result = webhooks.logs("wh-no-logs")

        assert result["webhook_id"] == "wh-no-logs"
        assert result["logs"] == []

    def test_logs_webhook_with_pagination(self, webhooks, mock_client):
        """Test logs() with pagination information."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "webhook_id": "wh-paginated",
            "logs": [
                {"timestamp": "2024-01-01T10:00:00Z", "status": "delivered"}
            ],
            "pagination": {
                "page": 1,
                "per_page": 10,
                "total": 25,
                "has_next": True
            }
        }
        mock_client._request.return_value = mock_response

        result = webhooks.logs("wh-paginated")

        assert result["pagination"]["total"] == 25
        assert result["pagination"]["has_next"] is True

    # ==================== Integration and Error Scenarios ====================

    def test_webhook_workflow_add_update_delete(self, webhooks, mock_client):
        """Test complete webhook workflow: add -> update -> delete."""
        # Mock responses for the sequence
        add_response = mock.MagicMock()
        add_response.json.return_value = {"status": "success", "webhook_id": "wh-workflow"}
        
        update_response = mock.MagicMock()
        update_response.json.return_value = {"status": "success", "webhook_id": "wh-workflow"}
        
        delete_response = mock.MagicMock()
        delete_response.json.return_value = {"status": "success", "webhook_id": "wh-workflow"}

        mock_client._request.side_effect = [add_response, update_response, delete_response]

        # Add webhook
        add_result = webhooks.add(
            webhook_url="https://example.com/webhook",
            event_types=["PIXELFLOW"]
        )
        webhook_id = add_result["webhook_id"]

        # Update webhook
        update_result = webhooks.update(
            webhook_id=webhook_id,
            webhook_url="https://updated.example.com/webhook",
            event_types=["PIXELFLOW", "GENERATION"]
        )

        # Delete webhook
        delete_result = webhooks.delete(webhook_id)

        assert add_result["status"] == "success"
        assert update_result["status"] == "success"
        assert delete_result["status"] == "success"
        assert mock_client._request.call_count == 3

    def test_webhook_api_error_handling(self, webhooks, mock_client):
        """Test error handling for various HTTP errors."""
        # Test 400 Bad Request
        mock_client._request.side_effect = httpx.HTTPStatusError(
            "Bad Request", 
            request=mock.MagicMock(),
            response=mock.MagicMock(status_code=400)
        )

        with pytest.raises(httpx.HTTPStatusError):
            webhooks.add(
                webhook_url="invalid-url",
                event_types=["INVALID_EVENT"]
            )

    def test_webhook_network_timeout(self, webhooks, mock_client):
        """Test webhook operations with network timeout."""
        mock_client._request.side_effect = httpx.TimeoutException("Request timed out")

        with pytest.raises(httpx.TimeoutException):
            webhooks.get()

    @pytest.mark.parametrize("webhook_url,event_types", [
        ("https://example.com/webhook", ["PIXELFLOW"]),
        ("http://localhost:3000/webhook", ["GENERATION"]),
        ("https://api.myapp.com/webhooks/segmind", ["PIXELFLOW", "GENERATION"]),
        ("https://webhook.site/unique-id", ["MODEL_INFERENCE"]),
    ])
    def test_add_webhook_various_urls_and_events(self, webhooks, mock_client, webhook_url, event_types):
        """Test adding webhooks with various URL formats and event types."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {"status": "success", "webhook_id": "wh-param-test"}
        mock_client._request.return_value = mock_response

        result = webhooks.add(webhook_url=webhook_url, event_types=event_types)

        assert result["status"] == "success"
        call_args = mock_client._request.call_args
        assert call_args[1]["json"]["webhook_url"] == webhook_url
        assert call_args[1]["json"]["event"]["types"] == event_types

    def test_webhook_base_url_usage(self, webhooks):
        """Test that the correct base URL is used for all operations."""
        assert webhooks.base_url == "https://api.spotprod.segmind.com/webhook"

    def test_webhook_response_json_parsing_error(self, webhooks, mock_client):
        """Test handling of JSON parsing errors in responses."""
        mock_response = mock.MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_client._request.return_value = mock_response

        with pytest.raises(ValueError):
            webhooks.get()

    def test_webhook_logs_with_detailed_error_info(self, webhooks, mock_client):
        """Test logs method with detailed error information."""
        detailed_logs = {
            "webhook_id": "wh-detailed-errors",
            "logs": [
                {
                    "timestamp": "2024-01-01T10:00:00Z",
                    "event_type": "PIXELFLOW",
                    "status": "failed",
                    "response_code": 500,
                    "response_time_ms": 30000,
                    "error": "Internal Server Error",
                    "retry_count": 3,
                    "next_retry_at": "2024-01-01T10:05:00Z"
                }
            ]
        }
        
        mock_response = mock.MagicMock()
        mock_response.json.return_value = detailed_logs
        mock_client._request.return_value = mock_response

        result = webhooks.logs("wh-detailed-errors")

        assert result["logs"][0]["retry_count"] == 3
        assert result["logs"][0]["next_retry_at"] == "2024-01-01T10:05:00Z"
        assert result["logs"][0]["error"] == "Internal Server Error"