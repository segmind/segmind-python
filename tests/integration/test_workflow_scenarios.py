"""Integration tests for complete workflow scenarios."""

import tempfile
from pathlib import Path
from unittest import mock

import pytest
import httpx

from segmind.client import SegmindClient
from segmind.exceptions import SegmindError


class TestCompleteWorkflows:
    """Integration tests for complete user workflows."""

    @pytest.fixture
    def client(self, mock_api_key):
        """Create a SegmindClient for testing."""
        return SegmindClient(api_key=mock_api_key)

    @pytest.fixture
    def temp_image(self):
        """Create a temporary image file for testing."""
        # Minimal PNG data
        png_data = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
            b'\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89'
            b'\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01'
            b'\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(png_data)
            temp_path = Path(f.name)
        
        yield temp_path
        temp_path.unlink(missing_ok=True)

    def test_text_to_image_workflow(self, client):
        """Test complete text-to-image generation workflow."""
        with mock.patch.object(client, '_client') as mock_client:
            # Mock successful model run
            mock_response = mock.MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "id": "gen_123",
                "status": "completed",
                "output": {
                    "image_url": "https://cdn.segmind.com/image_123.jpg",
                    "width": 1024,
                    "height": 768
                },
                "credits_used": 1.5
            }
            mock_client.post.return_value = mock_response

            # Run the model
            result = client.run(
                "text-to-image-v1",
                prompt="A beautiful sunset over mountains",
                aspect_ratio="16:9",
                quality="high"
            )

            # Verify the request was made correctly
            mock_client.post.assert_called_once_with(
                "/text-to-image-v1",
                json={
                    "prompt": "A beautiful sunset over mountains",
                    "aspect_ratio": "16:9",
                    "quality": "high"
                }
            )

            # Verify the response
            response_data = result.json()
            assert response_data["id"] == "gen_123"
            assert response_data["status"] == "completed"
            assert response_data["output"]["image_url"].startswith("https://")

    @pytest.mark.skip(reason="TODO: Fix mocking - client reference captured before patch applied")
    def test_file_upload_and_processing_workflow(self, client, temp_image):
        """Test workflow involving file upload and subsequent processing."""
        with mock.patch.object(client.files, '_client') as mock_files_client, \
             mock.patch.object(client, '_client') as mock_main_client:
            
            # Mock file upload
            upload_response = mock.MagicMock()
            upload_response.status_code = 200  # Set status code for raise_for_status
            upload_response.json.return_value = {
                "file_id": "file_123",
                "url": "https://cdn.segmind.com/uploads/file_123.png",
                "status": "processed"
            }
            mock_files_client._request.return_value = upload_response

            # Mock model processing
            process_response = mock.MagicMock()
            process_response.status_code = 200
            process_response.json.return_value = {
                "id": "proc_456",
                "status": "completed",
                "output": {
                    "processed_image_url": "https://cdn.segmind.com/processed_456.jpg"
                }
            }
            mock_main_client.post.return_value = process_response

            # Upload file
            upload_result = client.files.upload(temp_image)
            file_url = upload_result["url"]

            # Process the uploaded file
            process_result = client.run(
                "image-enhancement",
                input_image=file_url,
                enhancement_type="super_resolution"
            )

            # Verify both operations
            mock_files_client._request.assert_called_once()
            mock_main_client.post.assert_called_once_with(
                "/image-enhancement",
                json={
                    "input_image": file_url,
                    "enhancement_type": "super_resolution"
                }
            )

            assert upload_result["file_id"] == "file_123"
            assert process_result.json()["output"]["processed_image_url"].startswith("https://")

    @pytest.mark.skip(reason="TODO: Fix mocking - client reference captured before patch applied")
    def test_pixelflow_complete_workflow(self, client):
        """Test complete PixelFlow workflow with polling."""
        with mock.patch.object(client.pixelflows, '_client') as mock_client:
            # Mock initial workflow submission
            initial_response = mock.MagicMock()
            initial_response.status_code = 200  # Set status code for raise_for_status
            initial_response.json.return_value = {
                "request_id": "req_789",
                "status": "QUEUED",
                "poll_url": "https://api.segmind.com/workflows/request/req_789"
            }

            # Mock polling responses (queued -> processing -> completed)
            poll_responses = [
                {"status": "QUEUED"},
                {"status": "PROCESSING", "progress": 25},
                {"status": "PROCESSING", "progress": 75},
                {
                    "status": "COMPLETED",
                    "output": {
                        "workflow_result": "https://cdn.segmind.com/workflow_result.png",
                        "metadata": {"processing_time": 45}
                    }
                }
            ]

            mock_poll_responses = []
            for poll_data in poll_responses:
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200  # Set status code for raise_for_status
                mock_resp.json.return_value = poll_data
                mock_poll_responses.append(mock_resp)

            # Set up the mock call sequence
            mock_client._request.side_effect = [initial_response] + mock_poll_responses

            # Run the workflow with polling
            result = client.pixelflows.run(
                workflow_id="text-to-infographic",
                data={"text": "Market analysis report", "style": "modern"},
                poll=True,
                poll_interval=0.1,  # Fast polling for test
                max_wait_time=10
            )

            # Verify the workflow completed successfully
            assert result["status"] == "COMPLETED"
            assert "workflow_result" in result["output"]
            assert result["output"]["metadata"]["processing_time"] == 45

            # Verify polling occurred multiple times
            assert mock_client._request.call_count == 5  # 1 initial + 4 polls

    @pytest.mark.skip(reason="TODO: Fix mocking - client reference captured before patch applied")
    def test_webhook_setup_and_management_workflow(self, client):
        """Test complete webhook setup and management workflow."""
        with mock.patch.object(client.webhooks, '_client') as mock_client:
            # Mock webhook creation
            create_response = mock.MagicMock()
            create_response.status_code = 200  # Set status code for raise_for_status
            create_response.json.return_value = {
                "webhook_id": "wh_123",
                "status": "active",
                "webhook_url": "https://example.com/webhook",
                "event_types": ["PIXELFLOW"]
            }

            # Mock webhook listing
            list_response = mock.MagicMock()
            list_response.status_code = 200  # Set status code for raise_for_status
            list_response.json.return_value = {
                "webhooks": [
                    {
                        "webhook_id": "wh_123",
                        "webhook_url": "https://example.com/webhook",
                        "event_types": ["PIXELFLOW"],
                        "status": "active"
                    }
                ]
            }

            # Mock webhook update
            update_response = mock.MagicMock()
            update_response.status_code = 200  # Set status code for raise_for_status
            update_response.json.return_value = {
                "webhook_id": "wh_123",
                "status": "active",
                "webhook_url": "https://example.com/updated-webhook",
                "event_types": ["PIXELFLOW", "GENERATION"]
            }

            # Mock webhook logs
            logs_response = mock.MagicMock()
            logs_response.status_code = 200  # Set status code for raise_for_status
            logs_response.json.return_value = {
                "webhook_id": "wh_123",
                "logs": [
                    {
                        "timestamp": "2024-01-15T10:00:00Z",
                        "event_type": "PIXELFLOW",
                        "status": "delivered",
                        "response_code": 200
                    }
                ]
            }

            mock_client._request.side_effect = [
                create_response,
                list_response,
                update_response,
                logs_response
            ]

            # Create webhook
            create_result = client.webhooks.add(
                webhook_url="https://example.com/webhook",
                event_types=["PIXELFLOW"]
            )
            webhook_id = create_result["webhook_id"]

            # List webhooks
            list_result = client.webhooks.get()

            # Update webhook
            update_result = client.webhooks.update(
                webhook_id=webhook_id,
                webhook_url="https://example.com/updated-webhook",
                event_types=["PIXELFLOW", "GENERATION"]
            )

            # Get webhook logs
            logs_result = client.webhooks.logs(webhook_id)

            # Verify all operations
            assert create_result["webhook_id"] == "wh_123"
            assert len(list_result["webhooks"]) == 1
            assert "GENERATION" in update_result["event_types"]
            assert len(logs_result["logs"]) == 1

    @pytest.mark.skip(reason="TODO: Fix mocking - client reference captured before patch applied")
    def test_account_and_usage_monitoring_workflow(self, client):
        """Test account information and usage monitoring workflow."""
        with mock.patch.object(client.accounts, '_client') as mock_accounts_client, \
             mock.patch.object(client.generations, '_client') as mock_generations_client:
            
            # Mock account information
            account_response = mock.MagicMock()
            account_response.status_code = 200  # Set status code for raise_for_status
            account_response.json.return_value = {
                "user_id": "user_123",
                "subscription": {"plan": "pro", "status": "active"},
                "usage": {
                    "credits_balance": 150.5,
                    "credits_used_this_month": 49.5
                },
                "limits": {"max_credits_per_month": 500}
            }

            # Mock generations history
            generations_response = mock.MagicMock()
            generations_response.status_code = 200  # Set status code for raise_for_status
            generations_response.json.return_value = {
                "generations": [
                    {
                        "id": "gen_1",
                        "model": "text-to-image",
                        "credits_used": 1.5,
                        "created_at": "2024-01-15T10:00:00Z"
                    },
                    {
                        "id": "gen_2",
                        "model": "text-to-speech",
                        "credits_used": 0.5,
                        "created_at": "2024-01-15T09:30:00Z"
                    }
                ],
                "pagination": {"total": 2}
            }

            mock_accounts_client._request.return_value = account_response
            mock_generations_client._request.return_value = generations_response

            # Get account information
            account_info = client.accounts.current()

            # Get usage history
            usage_history = client.generations.get()

            # Analyze usage
            total_credits_used = sum(
                gen["credits_used"] for gen in usage_history["generations"]
            )
            credits_remaining = account_info["usage"]["credits_balance"]

            # Verify the workflow
            assert account_info["subscription"]["plan"] == "pro"
            assert total_credits_used == 2.0
            assert credits_remaining == 150.5
            assert len(usage_history["generations"]) == 2

    def test_error_handling_workflow(self, client):
        """Test error handling across different operations."""
        with mock.patch.object(client, '_client') as mock_client:
            # Mock API error response
            mock_client.post.side_effect = httpx.HTTPStatusError(
                "Rate limit exceeded",
                request=mock.MagicMock(),
                response=mock.MagicMock(status_code=429)
            )

            # Test error handling in model run
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                client.run("text-to-image", prompt="test prompt")

            assert exc_info.value.response.status_code == 429

    @pytest.mark.skip(reason="TODO: Fix mocking - client reference captured before patch applied")
    def test_concurrent_operations_workflow(self, client):
        """Test handling multiple concurrent operations."""
        import threading
        import time

        results = []
        errors = []

        def worker(worker_id):
            try:
                with mock.patch.object(client, '_client') as mock_client:
                    # Mock response with worker-specific data
                    mock_response = mock.MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "id": f"gen_{worker_id}",
                        "status": "completed",
                        "worker_id": worker_id
                    }
                    mock_client.post.return_value = mock_response

                    # Simulate processing time
                    time.sleep(0.1)

                    result = client.run(
                        "fast-model",
                        prompt=f"Test prompt {worker_id}",
                        worker_id=worker_id
                    )
                    results.append(result.json())

            except Exception as e:
                errors.append(e)

        # Create and start multiple threads
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()

        # Verify concurrent operations
        assert len(errors) == 0
        assert len(results) == 5
        for i, result in enumerate(results):
            assert result["worker_id"] == i

    @pytest.mark.skip(reason="TODO: Fix mocking - client reference captured before patch applied")
    def test_model_discovery_and_selection_workflow(self, client):
        """Test model discovery and selection workflow."""
        with mock.patch.object(client.models, '_client') as mock_client:
            # Mock models list response
            models_response = mock.MagicMock()
            models_response.status_code = 200  # Set status code for raise_for_status
            models_response.json.return_value = {
                "models": [
                    {
                        "id": "text-to-image-v1",
                        "name": "Text to Image v1",
                        "category": "text-to-image",
                        "pricing": {"credits_per_generation": 1.0}
                    },
                    {
                        "id": "text-to-image-v2",
                        "name": "Text to Image v2",
                        "category": "text-to-image",
                        "pricing": {"credits_per_generation": 1.5}
                    },
                    {
                        "id": "text-to-speech-v1",
                        "name": "Text to Speech v1",
                        "category": "text-to-speech",
                        "pricing": {"credits_per_second": 0.1}
                    }
                ],
                "categories": ["text-to-image", "text-to-speech"]
            }
            mock_client._request.return_value = models_response

            # Discover available models
            models_info = client.models.get()

            # Filter models by category
            text_to_image_models = [
                model for model in models_info["models"]
                if model["category"] == "text-to-image"
            ]

            # Select most cost-effective model
            cheapest_model = min(
                text_to_image_models,
                key=lambda m: m["pricing"]["credits_per_generation"]
            )

            # Verify model discovery workflow
            assert len(models_info["models"]) == 3
            assert len(text_to_image_models) == 2
            assert cheapest_model["id"] == "text-to-image-v1"
            assert cheapest_model["pricing"]["credits_per_generation"] == 1.0

    def test_batch_processing_workflow(self, client):
        """Test batch processing of multiple requests."""
        with mock.patch.object(client, '_client') as mock_client:
            # Mock responses for batch processing
            mock_responses = []
            for i in range(3):
                mock_resp = mock.MagicMock()
                mock_resp.status_code = 200
                mock_resp.json.return_value = {
                    "id": f"batch_gen_{i}",
                    "status": "completed",
                    "output": f"result_{i}.jpg"
                }
                mock_responses.append(mock_resp)

            mock_client.post.side_effect = mock_responses

            # Process batch of requests
            prompts = [
                "A red car",
                "A blue house",
                "A green tree"
            ]

            results = []
            for i, prompt in enumerate(prompts):
                result = client.run(
                    "text-to-image",
                    prompt=prompt,
                    batch_id=i
                )
                results.append(result.json())

            # Verify batch processing
            assert len(results) == 3
            for i, result in enumerate(results):
                assert result["id"] == f"batch_gen_{i}"
                assert result["output"] == f"result_{i}.jpg"

    @pytest.mark.skip(reason="TODO: Fix mocking - client reference captured before patch applied")
    def test_resource_cleanup_workflow(self, client, temp_image):
        """Test resource cleanup and management workflow."""
        with mock.patch.object(client.files, '_client') as mock_files_client, \
             mock.patch.object(client.webhooks, '_client') as mock_webhooks_client:
            
            # Mock file upload
            upload_response = mock.MagicMock()
            upload_response.status_code = 200  # Set status code for raise_for_status
            upload_response.json.return_value = {
                "file_id": "temp_file_123",
                "expires_at": "2024-01-16T00:00:00Z"
            }

            # Mock webhook deletion
            delete_response = mock.MagicMock()
            delete_response.status_code = 200  # Set status code for raise_for_status
            delete_response.json.return_value = {
                "webhook_id": "temp_wh_456",
                "status": "inactive"
            }

            mock_files_client._request.return_value = upload_response
            mock_webhooks_client._request.return_value = delete_response

            try:
                # Upload temporary file
                upload_result = client.files.upload(temp_image)
                file_id = upload_result["file_id"]

                # Create temporary webhook
                webhook_result = client.webhooks.add(
                    webhook_url="https://temp.example.com/webhook",
                    event_types=["PIXELFLOW"]
                )
                # webhook_id would be extracted from webhook_result in real scenario

                # Verify resources were created
                assert upload_result["file_id"] == "temp_file_123"

            finally:
                # Cleanup: delete temporary webhook
                cleanup_result = client.webhooks.delete("temp_wh_456")
                assert cleanup_result["status"] == "inactive"