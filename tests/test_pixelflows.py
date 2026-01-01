"""Comprehensive tests for the PixelFlows module."""

import json
import time
from unittest import mock

import pytest

from segmind.pixelflows import PixelFlows


class TestPixelFlows:
    """Test cases for the PixelFlows class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = mock.MagicMock()
        client._request = mock.MagicMock()
        return client

    @pytest.fixture
    def pixelflows(self, mock_client):
        """Create a PixelFlows instance with mock client."""
        pf = PixelFlows(client=mock_client)
        pf._client = mock_client
        pf.client = mock_client
        return pf

    # ==================== Test run() method ====================

    def test_run_with_workflow_id_success(self, pixelflows, mock_client):
        """Test successful workflow run with workflow_id."""
        # Mock initial POST response
        initial_response = mock.MagicMock()
        initial_response.json.return_value = {
            "request_id": "req-123",
            "poll_url": "https://api.segmind.com/workflows/request/req-123",
            "status": "QUEUED"
        }

        # Mock polling responses
        poll_response_queued = mock.MagicMock()
        poll_response_queued.json.return_value = {"status": "QUEUED"}

        poll_response_processing = mock.MagicMock()
        poll_response_processing.json.return_value = {"status": "PROCESSING"}

        poll_response_completed = mock.MagicMock()
        poll_response_completed.json.return_value = {
            "status": "COMPLETED",
            "output": {"result": "success", "data": "generated_image.png"}
        }

        # Set up the mock to return different responses
        mock_client._request.side_effect = [
            initial_response,
            poll_response_queued,
            poll_response_processing,
            poll_response_completed
        ]

        result = pixelflows.run(
            workflow_id="test-workflow",
            data={"prompt": "test prompt"},
            poll=True,
            poll_interval=0.1  # Fast polling for tests
        )

        assert result["status"] == "COMPLETED"
        assert result["output"]["result"] == "success"
        assert mock_client._request.call_count == 4

    def test_run_with_workflow_url_success(self, pixelflows, mock_client):
        """Test successful workflow run with workflow_url."""
        initial_response = mock.MagicMock()
        initial_response.json.return_value = {
            "request_id": "req-456",
            "status": "COMPLETED",
            "output": {"result": "immediate_success"}
        }
        mock_client._request.return_value = initial_response

        result = pixelflows.run(
            workflow_url="https://custom.api.com/workflow/123",
            data={"input": "test"},
            poll=False
        )

        assert result["status"] == "COMPLETED"
        assert result["output"]["result"] == "immediate_success"
        mock_client._request.assert_called_once_with(
            "POST",
            "https://custom.api.com/workflow/123",
            json={"input": "test"}
        )

    def test_run_without_workflow_id_or_url_raises_error(self, pixelflows):
        """Test that run() raises ValueError without workflow_id or workflow_url."""
        with pytest.raises(ValueError, match="Either workflow_id or workflow_url must be provided"):
            pixelflows.run(data={"test": "data"})

    def test_run_with_poll_disabled(self, pixelflows, mock_client):
        """Test workflow run without polling."""
        initial_response = mock.MagicMock()
        initial_response.json.return_value = {
            "request_id": "req-789",
            "status": "QUEUED"
        }
        mock_client._request.return_value = initial_response

        result = pixelflows.run(
            workflow_id="test-workflow",
            data={"prompt": "test"},
            poll=False
        )

        assert result["status"] == "QUEUED"
        assert result["request_id"] == "req-789"
        mock_client._request.assert_called_once()

    def test_run_with_timeout(self, pixelflows, mock_client):
        """Test workflow run that times out."""
        initial_response = mock.MagicMock()
        initial_response.json.return_value = {
            "request_id": "req-timeout",
            "poll_url": "https://api.segmind.com/workflows/request/req-timeout",
            "status": "QUEUED"
        }

        poll_response = mock.MagicMock()
        poll_response.json.return_value = {"status": "PROCESSING"}

        mock_client._request.side_effect = [initial_response] + [poll_response] * 10

        result = pixelflows.run(
            workflow_id="slow-workflow",
            data={"prompt": "test"},
            poll=True,
            poll_interval=0.1,
            max_wait_time=0.5
        )

        assert result["status"] == "TIMEOUT"
        assert "timed out after" in result["error_message"]

    def test_run_with_failed_status(self, pixelflows, mock_client):
        """Test workflow run that fails."""
        initial_response = mock.MagicMock()
        initial_response.json.return_value = {
            "request_id": "req-fail",
            "poll_url": "https://api.segmind.com/workflows/request/req-fail",
            "status": "QUEUED"
        }

        poll_response_failed = mock.MagicMock()
        poll_response_failed.json.return_value = {
            "status": "FAILED",
            "error": "Processing error occurred"
        }

        mock_client._request.side_effect = [initial_response, poll_response_failed]

        result = pixelflows.run(
            workflow_id="failing-workflow",
            data={"prompt": "test"},
            poll=True,
            poll_interval=0.1
        )

        assert result["status"] == "FAILED"
        assert result["error"] == "Processing error occurred"

    def test_run_with_json_string_output(self, pixelflows, mock_client):
        """Test workflow run that returns JSON string in output."""
        initial_response = mock.MagicMock()
        initial_response.json.return_value = {
            "request_id": "req-json",
            "poll_url": "https://api.segmind.com/workflows/request/req-json",
            "status": "QUEUED"
        }

        poll_response_completed = mock.MagicMock()
        poll_response_completed.json.return_value = {
            "status": "COMPLETED",
            "output": '{"nested": {"data": "value"}, "array": [1, 2, 3]}'
        }

        mock_client._request.side_effect = [initial_response, poll_response_completed]

        result = pixelflows.run(
            workflow_id="json-workflow",
            data={"prompt": "test"},
            poll=True,
            poll_interval=0.1
        )

        assert result["status"] == "COMPLETED"
        assert isinstance(result["output"], dict)
        assert result["output"]["nested"]["data"] == "value"
        assert result["output"]["array"] == [1, 2, 3]

    def test_run_with_invalid_json_string_output(self, pixelflows, mock_client):
        """Test workflow run with invalid JSON string in output."""
        initial_response = mock.MagicMock()
        initial_response.json.return_value = {
            "request_id": "req-invalid-json",
            "poll_url": "https://api.segmind.com/workflows/request/req-invalid-json",
            "status": "QUEUED"
        }

        poll_response_completed = mock.MagicMock()
        poll_response_completed.json.return_value = {
            "status": "COMPLETED",
            "output": "This is not valid JSON {broken:"
        }

        mock_client._request.side_effect = [initial_response, poll_response_completed]

        result = pixelflows.run(
            workflow_id="invalid-json-workflow",
            data={"prompt": "test"},
            poll=True,
            poll_interval=0.1
        )

        assert result["status"] == "COMPLETED"
        assert isinstance(result["output"], str)
        assert result["output"] == "This is not valid JSON {broken:"

    def test_run_without_poll_url_or_id(self, pixelflows, mock_client):
        """Test workflow run when response doesn't have poll_url or request_id."""
        initial_response = mock.MagicMock()
        initial_response.json.return_value = {
            "status": "COMPLETED",
            "output": "Direct result"
        }
        mock_client._request.return_value = initial_response

        result = pixelflows.run(
            workflow_id="instant-workflow",
            data={"prompt": "test"},
            poll=True
        )

        assert result["status"] == "COMPLETED"
        assert result["output"] == "Direct result"
        mock_client._request.assert_called_once()

    def test_run_with_empty_data(self, pixelflows, mock_client):
        """Test workflow run with no data parameter."""
        initial_response = mock.MagicMock()
        initial_response.json.return_value = {
            "status": "COMPLETED",
            "output": "Success"
        }
        mock_client._request.return_value = initial_response

        result = pixelflows.run(workflow_id="simple-workflow", poll=False)

        assert result["status"] == "COMPLETED"
        mock_client._request.assert_called_once_with(
            "POST",
            "https://api.segmind.com/workflows/simple-workflow",
            json={}
        )

    # ==================== Test get_status() method ====================

    def test_get_status_with_poll_id(self, pixelflows, mock_client):
        """Test get_status with poll_id."""
        response = mock.MagicMock()
        response.json.return_value = {
            "status": "PROCESSING",
            "progress": 50
        }
        mock_client._request.return_value = response

        # Mock the workflows_base property
        pixelflows.workflows_base = "https://api.segmind.com/workflows"

        result = pixelflows.get_status(poll_id="req-status-123")

        assert result["status"] == "PROCESSING"
        assert result["progress"] == 50
        mock_client._request.assert_called_once_with(
            "GET",
            "https://api.segmind.com/workflows/request/req-status-123"
        )

    def test_get_status_with_poll_url(self, pixelflows, mock_client):
        """Test get_status with poll_url."""
        response = mock.MagicMock()
        response.json.return_value = {
            "status": "COMPLETED",
            "output": {"result": "done"}
        }
        mock_client._request.return_value = response

        result = pixelflows.get_status(poll_url="https://custom.api.com/status/456")

        assert result["status"] == "COMPLETED"
        assert result["output"]["result"] == "done"
        mock_client._request.assert_called_once_with(
            "GET",
            "https://custom.api.com/status/456"
        )

    def test_get_status_without_poll_id_or_url_raises_error(self, pixelflows):
        """Test that get_status raises ValueError without poll_id or poll_url."""
        with pytest.raises(ValueError, match="Either poll_id or poll_url must be provided"):
            pixelflows.get_status()

    def test_get_status_with_both_poll_id_and_url_raises_error(self, pixelflows):
        """Test that get_status raises ValueError with both poll_id and poll_url."""
        with pytest.raises(ValueError, match="Only one of poll_id or poll_url should be provided"):
            pixelflows.get_status(
                poll_id="req-123",
                poll_url="https://api.com/status/456"
            )

    def test_get_status_with_json_string_output(self, pixelflows, mock_client):
        """Test get_status with JSON string in output."""
        response = mock.MagicMock()
        response.json.return_value = {
            "status": "COMPLETED",
            "output": '{"parsed": "json", "number": 42}'
        }
        mock_client._request.return_value = response

        pixelflows.workflows_base = "https://api.segmind.com/workflows"
        result = pixelflows.get_status(poll_id="req-json-status")

        assert result["status"] == "COMPLETED"
        assert isinstance(result["output"], dict)
        assert result["output"]["parsed"] == "json"
        assert result["output"]["number"] == 42

    # ==================== Test poll() method ====================

    def test_poll_with_poll_id_success(self, pixelflows, mock_client):
        """Test successful polling with poll_id."""
        poll_response_processing = mock.MagicMock()
        poll_response_processing.json.return_value = {"status": "PROCESSING"}

        poll_response_completed = mock.MagicMock()
        poll_response_completed.json.return_value = {
            "status": "COMPLETED",
            "output": {"result": "success"}
        }

        mock_client._request.side_effect = [
            poll_response_processing,
            poll_response_completed
        ]

        pixelflows.workflows_base = "https://api.segmind.com/workflows"
        result = pixelflows.poll(poll_id="req-poll-123", poll_interval=0.1)

        assert result["status"] == "COMPLETED"
        assert result["output"]["result"] == "success"
        assert mock_client._request.call_count == 2

    def test_poll_with_poll_url_success(self, pixelflows, mock_client):
        """Test successful polling with poll_url."""
        poll_response_completed = mock.MagicMock()
        poll_response_completed.json.return_value = {
            "status": "COMPLETED",
            "output": "Direct result"
        }

        mock_client._request.return_value = poll_response_completed

        result = pixelflows.poll(
            poll_url="https://api.segmind.com/status/456",
            poll_interval=0.1
        )

        assert result["status"] == "COMPLETED"
        assert result["output"] == "Direct result"

    def test_poll_without_poll_id_or_url_raises_error(self, pixelflows):
        """Test that poll raises ValueError without poll_id or poll_url."""
        with pytest.raises(ValueError, match="Either poll_id or poll_url must be provided"):
            pixelflows.poll()

    def test_poll_with_timeout(self, pixelflows, mock_client):
        """Test polling that times out."""
        poll_response = mock.MagicMock()
        poll_response.json.return_value = {"status": "PROCESSING"}

        mock_client._request.return_value = poll_response
        pixelflows.workflows_base = "https://api.segmind.com/workflows"

        result = pixelflows.poll(
            poll_id="req-timeout",
            poll_interval=0.1,
            max_wait_time=0.3
        )

        assert result["status"] == "TIMEOUT"
        assert "timed out after" in result["error_message"]

    # ==================== Test _poll_for_results() method ====================

    def test_poll_for_results_immediate_completion(self, pixelflows, mock_client):
        """Test _poll_for_results with immediate completion."""
        response = mock.MagicMock()
        response.json.return_value = {
            "status": "COMPLETED",
            "output": {"immediate": "result"}
        }
        mock_client._request.return_value = response

        result = pixelflows._poll_for_results(
            "https://api.com/poll",
            poll_interval=1,
            max_wait_time=10
        )

        assert result["status"] == "COMPLETED"
        assert result["output"]["immediate"] == "result"
        mock_client._request.assert_called_once()

    def test_poll_for_results_multiple_statuses(self, pixelflows, mock_client):
        """Test _poll_for_results with various status transitions."""
        responses = [
            {"status": "QUEUED"},
            {"status": "PROCESSING", "progress": 25},
            {"status": "PROCESSING", "progress": 75},
            {"status": "COMPLETED", "output": "Final result"}
        ]

        mock_responses = []
        for resp in responses:
            mock_resp = mock.MagicMock()
            mock_resp.json.return_value = resp
            mock_responses.append(mock_resp)

        mock_client._request.side_effect = mock_responses

        result = pixelflows._poll_for_results(
            "https://api.com/poll",
            poll_interval=0.01,
            max_wait_time=10
        )

        assert result["status"] == "COMPLETED"
        assert result["output"] == "Final result"
        assert mock_client._request.call_count == 4

    def test_poll_for_results_unknown_status(self, pixelflows, mock_client):
        """Test _poll_for_results with unknown status."""
        response = mock.MagicMock()
        response.json.return_value = {
            "status": "UNKNOWN_STATUS",
            "message": "Something unexpected"
        }
        mock_client._request.return_value = response

        result = pixelflows._poll_for_results(
            "https://api.com/poll",
            poll_interval=1,
            max_wait_time=10
        )

        assert result["status"] == "UNKNOWN_STATUS"
        assert result["message"] == "Something unexpected"
        mock_client._request.assert_called_once()

    def test_poll_for_results_failed_status(self, pixelflows, mock_client):
        """Test _poll_for_results with failed status."""
        queued_response = mock.MagicMock()
        queued_response.json.return_value = {"status": "QUEUED"}

        failed_response = mock.MagicMock()
        failed_response.json.return_value = {
            "status": "FAILED",
            "error": "Processing failed",
            "error_code": "E001"
        }

        mock_client._request.side_effect = [queued_response, failed_response]

        result = pixelflows._poll_for_results(
            "https://api.com/poll",
            poll_interval=0.01,
            max_wait_time=10
        )

        assert result["status"] == "FAILED"
        assert result["error"] == "Processing failed"
        assert result["error_code"] == "E001"

    # ==================== Edge cases and error scenarios ====================

    def test_run_with_network_error(self, pixelflows, mock_client):
        """Test run method when network error occurs."""
        import httpx
        mock_client._request.side_effect = httpx.NetworkError("Connection failed")

        with pytest.raises(httpx.NetworkError):
            pixelflows.run(workflow_id="test-workflow", data={"test": "data"})

    def test_poll_with_malformed_response(self, pixelflows, mock_client):
        """Test polling with malformed API response."""
        response = mock.MagicMock()
        response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_client._request.return_value = response

        pixelflows.workflows_base = "https://api.segmind.com/workflows"

        with pytest.raises(json.JSONDecodeError):
            pixelflows.poll(poll_id="req-malformed")

    @pytest.mark.parametrize("poll_interval,max_wait_time", [
        (0.5, 2),
        (1, 5),
        (2, 10),
    ])
    def test_poll_timing_parameters(self, pixelflows, mock_client, poll_interval, max_wait_time):
        """Test polling with different timing parameters."""
        start_time = time.time()

        # Mock response that never completes
        response = mock.MagicMock()
        response.json.return_value = {"status": "PROCESSING"}
        mock_client._request.return_value = response

        result = pixelflows._poll_for_results(
            "https://api.com/poll",
            poll_interval=poll_interval,
            max_wait_time=max_wait_time
        )

        elapsed_time = time.time() - start_time

        assert result["status"] == "TIMEOUT"
        assert elapsed_time >= max_wait_time
        assert elapsed_time < max_wait_time + poll_interval + 0.5  # Some buffer for execution

    def test_run_url_construction_with_workflow_id(self, pixelflows, mock_client):
        """Test that URL is correctly constructed with workflow_id."""
        response = mock.MagicMock()
        response.json.return_value = {"status": "COMPLETED"}
        mock_client._request.return_value = response

        pixelflows.run(workflow_id="my-workflow-123", poll=False)

        mock_client._request.assert_called_once_with(
            "POST",
            "https://api.segmind.com/workflows/my-workflow-123",
            json={}
        )

    def test_run_preserves_custom_workflow_url(self, pixelflows, mock_client):
        """Test that custom workflow_url is preserved."""
        response = mock.MagicMock()
        response.json.return_value = {"status": "COMPLETED"}
        mock_client._request.return_value = response

        custom_url = "https://custom.domain.com/my/workflow/endpoint"
        pixelflows.run(workflow_url=custom_url, poll=False)

        mock_client._request.assert_called_once_with(
            "POST",
            custom_url,
            json={}
        )
