"""Mock response fixtures for testing API interactions."""

from typing import Any, Dict, List, Optional
from unittest import mock

import pytest
import httpx


@pytest.fixture
def mock_success_response():
    """Create a mock successful HTTP response."""
    response = mock.MagicMock(spec=httpx.Response)
    response.status_code = 200
    response.json.return_value = {"status": "success", "message": "Operation completed"}
    return response


@pytest.fixture
def mock_error_response():
    """Create a mock error HTTP response."""
    response = mock.MagicMock(spec=httpx.Response)
    response.status_code = 400
    response.json.return_value = {"error": "Bad Request", "detail": "Invalid parameters"}
    return response


@pytest.fixture
def sample_model_inference_response():
    """Sample response for model inference requests."""
    return {
        "id": "inf_1234567890",
        "model": "seedream-v3-text-to-image",
        "status": "completed",
        "created_at": "2024-01-15T10:30:00Z",
        "completed_at": "2024-01-15T10:30:45Z",
        "output": {
            "image_url": "https://cdn.segmind.com/generated/abc123.jpg",
            "width": 1024,
            "height": 768,
            "format": "JPEG",
            "seed": 42
        },
        "usage": {
            "credits_used": 1.5,
            "processing_time_ms": 45000
        },
        "parameters": {
            "prompt": "A beautiful sunset over mountains",
            "aspect_ratio": "16:9",
            "quality": "high"
        }
    }


@pytest.fixture
def sample_pixelflow_response():
    """Sample response for PixelFlow requests."""
    return {
        "request_id": "req_9876543210",
        "workflow_id": "wf_text_to_infographic",
        "status": "queued",
        "created_at": "2024-01-15T11:00:00Z",
        "poll_url": "https://api.segmind.com/workflows/request/req_9876543210",
        "estimated_wait_time": 30,
        "queue_position": 3
    }


@pytest.fixture
def sample_pixelflow_completed_response():
    """Sample completed PixelFlow response."""
    return {
        "request_id": "req_9876543210",
        "workflow_id": "wf_text_to_infographic",
        "status": "COMPLETED",
        "created_at": "2024-01-15T11:00:00Z",
        "completed_at": "2024-01-15T11:02:15Z",
        "output": {
            "infographic_url": "https://cdn.segmind.com/workflows/infographic_123.png",
            "components": [
                {"type": "title", "text": "Market Analysis 2024"},
                {"type": "chart", "chart_type": "bar", "data_points": 5},
                {"type": "summary", "word_count": 150}
            ]
        },
        "metadata": {
            "processing_time": 135,
            "credits_used": 2.5,
            "quality_score": 0.95
        }
    }


@pytest.fixture
def sample_file_upload_response():
    """Sample response for file upload requests."""
    return {
        "file_id": "file_abcdef123456",
        "filename": "uploaded_image.png",
        "original_filename": "my_image.png",
        "url": "https://cdn.segmind.com/uploads/file_abcdef123456",
        "content_type": "image/png",
        "size_bytes": 245760,
        "width": 1920,
        "height": 1080,
        "upload_time": "2024-01-15T12:15:30Z",
        "expires_at": "2024-01-22T12:15:30Z",
        "status": "processed",
        "checksum": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    }


@pytest.fixture
def sample_webhook_response():
    """Sample response for webhook operations."""
    return {
        "webhook_id": "wh_789012345",
        "webhook_url": "https://example.com/segmind-webhook",
        "event_types": ["PIXELFLOW", "GENERATION"],
        "status": "active",
        "created_at": "2024-01-10T09:00:00Z",
        "last_delivery": {
            "timestamp": "2024-01-15T14:20:00Z",
            "status": "delivered",
            "response_code": 200,
            "response_time_ms": 120
        },
        "delivery_stats": {
            "total_deliveries": 45,
            "successful_deliveries": 43,
            "failed_deliveries": 2,
            "average_response_time_ms": 95
        }
    }


@pytest.fixture
def sample_account_response():
    """Sample response for account information."""
    return {
        "user_id": "user_abc123def456",
        "email": "user@example.com",
        "username": "example_user",
        "first_name": "John",
        "last_name": "Doe",
        "account_type": "pro",
        "subscription": {
            "plan": "pro",
            "status": "active",
            "created_at": "2023-06-15T00:00:00Z",
            "expires_at": "2024-06-15T00:00:00Z",
            "auto_renew": True
        },
        "usage": {
            "credits_balance": 150.5,
            "credits_used_this_month": 49.5,
            "api_calls_this_month": 127,
            "storage_used_mb": 245.7
        },
        "limits": {
            "max_credits_per_month": 500,
            "max_api_calls_per_minute": 60,
            "max_storage_mb": 1000,
            "max_file_size_mb": 50
        },
        "preferences": {
            "timezone": "UTC",
            "notifications_enabled": True,
            "newsletter_subscription": False
        },
        "last_login": "2024-01-15T08:30:00Z"
    }


@pytest.fixture
def sample_generations_response():
    """Sample response for generations list."""
    return {
        "generations": [
            {
                "id": "gen_123",
                "model": "text-to-image-v1",
                "status": "completed",
                "created_at": "2024-01-15T10:00:00Z",
                "prompt": "A cat wearing a hat",
                "output_url": "https://cdn.segmind.com/gen_123.jpg",
                "credits_used": 1.0
            },
            {
                "id": "gen_124",
                "model": "text-to-speech-v2",
                "status": "completed",
                "created_at": "2024-01-15T09:30:00Z",
                "prompt": "Hello world",
                "output_url": "https://cdn.segmind.com/gen_124.mp3",
                "credits_used": 0.5
            }
        ],
        "pagination": {
            "page": 1,
            "per_page": 10,
            "total": 25,
            "total_pages": 3,
            "has_next": True,
            "has_prev": False
        },
        "filters_applied": {
            "status": "completed",
            "date_range": "last_7_days"
        }
    }


@pytest.fixture
def sample_models_response():
    """Sample response for models list."""
    return {
        "models": [
            {
                "id": "seedream-v3-text-to-image",
                "name": "Seedream v3 Text to Image",
                "description": "Generate high-quality images from text descriptions",
                "category": "text-to-image",
                "version": "3.0",
                "status": "active",
                "pricing": {
                    "credits_per_generation": 1.5,
                    "estimated_time_seconds": 15
                },
                "parameters": {
                    "prompt": {"type": "string", "required": True},
                    "aspect_ratio": {"type": "string", "default": "1:1", "options": ["1:1", "16:9", "9:16"]},
                    "quality": {"type": "string", "default": "standard", "options": ["standard", "high"]}
                },
                "limits": {
                    "max_prompt_length": 500,
                    "max_generations_per_minute": 10
                }
            },
            {
                "id": "voice-synthesis-v2",
                "name": "Voice Synthesis v2",
                "description": "Convert text to natural-sounding speech",
                "category": "text-to-speech",
                "version": "2.1",
                "status": "active",
                "pricing": {
                    "credits_per_second": 0.1,
                    "estimated_time_seconds": 5
                },
                "parameters": {
                    "text": {"type": "string", "required": True},
                    "voice": {"type": "string", "default": "neutral", "options": ["male", "female", "neutral"]},
                    "speed": {"type": "float", "default": 1.0, "min": 0.5, "max": 2.0}
                }
            }
        ],
        "categories": ["text-to-image", "text-to-speech", "image-to-image", "audio-processing"],
        "total_models": 2
    }


@pytest.fixture
def error_responses():
    """Collection of various error responses."""
    return {
        "bad_request": {
            "status_code": 400,
            "response": {
                "error": "BAD_REQUEST",
                "detail": "Invalid parameters provided",
                "validation_errors": [
                    {"field": "prompt", "message": "Prompt is required"},
                    {"field": "model", "message": "Invalid model specified"}
                ]
            }
        },
        "unauthorized": {
            "status_code": 401,
            "response": {
                "error": "UNAUTHORIZED",
                "detail": "Invalid API key",
                "help_url": "https://docs.segmind.com/authentication"
            }
        },
        "forbidden": {
            "status_code": 403,
            "response": {
                "error": "FORBIDDEN",
                "detail": "Insufficient permissions",
                "required_plan": "pro"
            }
        },
        "not_found": {
            "status_code": 404,
            "response": {
                "error": "NOT_FOUND",
                "detail": "Resource not found",
                "resource_type": "model"
            }
        },
        "rate_limited": {
            "status_code": 429,
            "response": {
                "error": "RATE_LIMITED",
                "detail": "Rate limit exceeded",
                "limit": 60,
                "remaining": 0,
                "reset_time": "2024-01-15T15:01:00Z"
            }
        },
        "server_error": {
            "status_code": 500,
            "response": {
                "error": "INTERNAL_SERVER_ERROR",
                "detail": "An unexpected error occurred",
                "request_id": "req_error_123456"
            }
        },
        "service_unavailable": {
            "status_code": 503,
            "response": {
                "error": "SERVICE_UNAVAILABLE",
                "detail": "Service temporarily unavailable",
                "retry_after": 300
            }
        }
    }


@pytest.fixture
def webhook_event_samples():
    """Sample webhook event payloads."""
    return {
        "pixelflow_completed": {
            "event_type": "PIXELFLOW",
            "event_id": "evt_pixelflow_123",
            "timestamp": "2024-01-15T11:05:00Z",
            "data": {
                "request_id": "req_9876543210",
                "workflow_id": "wf_text_to_infographic",
                "status": "COMPLETED",
                "output": {
                    "infographic_url": "https://cdn.segmind.com/workflows/infographic_123.png"
                },
                "credits_used": 2.5
            }
        },
        "generation_completed": {
            "event_type": "GENERATION",
            "event_id": "evt_generation_456",
            "timestamp": "2024-01-15T10:35:00Z",
            "data": {
                "generation_id": "gen_123",
                "model": "text-to-image-v1",
                "status": "completed",
                "output_url": "https://cdn.segmind.com/gen_123.jpg",
                "credits_used": 1.0
            }
        },
        "generation_failed": {
            "event_type": "GENERATION",
            "event_id": "evt_generation_789",
            "timestamp": "2024-01-15T10:40:00Z",
            "data": {
                "generation_id": "gen_124",
                "model": "text-to-image-v1",
                "status": "failed",
                "error": "CONTENT_POLICY_VIOLATION",
                "error_detail": "Content violates usage policy"
            }
        }
    }


@pytest.fixture
def pagination_responses():
    """Sample paginated responses."""
    return {
        "page_1": {
            "data": [{"id": i, "name": f"Item {i}"} for i in range(1, 11)],
            "pagination": {
                "page": 1,
                "per_page": 10,
                "total": 25,
                "total_pages": 3,
                "has_next": True,
                "has_prev": False,
                "next_url": "/api/items?page=2",
                "prev_url": None
            }
        },
        "page_2": {
            "data": [{"id": i, "name": f"Item {i}"} for i in range(11, 21)],
            "pagination": {
                "page": 2,
                "per_page": 10,
                "total": 25,
                "total_pages": 3,
                "has_next": True,
                "has_prev": True,
                "next_url": "/api/items?page=3",
                "prev_url": "/api/items?page=1"
            }
        },
        "page_3": {
            "data": [{"id": i, "name": f"Item {i}"} for i in range(21, 26)],
            "pagination": {
                "page": 3,
                "per_page": 10,
                "total": 25,
                "total_pages": 3,
                "has_next": False,
                "has_prev": True,
                "next_url": None,
                "prev_url": "/api/items?page=2"
            }
        }
    }


@pytest.fixture
def mock_httpx_client():
    """Mock httpx.Client for testing."""
    client = mock.MagicMock(spec=httpx.Client)
    client.headers = {"User-Agent": "segmind-python/0.1.0"}
    client.timeout = mock.MagicMock()
    client.timeout.read = 30.0
    client.timeout.connect = 5.0
    return client


@pytest.fixture
def create_mock_response():
    """Factory for creating mock HTTP responses."""
    def _create_response(
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text_data: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> mock.MagicMock:
        response = mock.MagicMock(spec=httpx.Response)
        response.status_code = status_code
        
        if json_data is not None:
            response.json.return_value = json_data
        elif text_data is not None:
            response.text = text_data
            response.json.side_effect = ValueError("No JSON object could be decoded")
        
        if headers:
            response.headers = headers
        else:
            response.headers = {"content-type": "application/json"}
        
        return response
    
    return _create_response


@pytest.fixture
def api_endpoints():
    """Dictionary of API endpoints used in the SDK."""
    return {
        "models": {
            "list": "/models",
            "get": "/models/{model_id}",
            "run": "/{model_slug}"
        },
        "pixelflows": {
            "run": "https://api.segmind.com/workflows/{workflow_id}",
            "status": "https://api.segmind.com/workflows/request/{request_id}",
            "custom": "{workflow_url}"
        },
        "files": {
            "upload": "https://api.spotprod.segmind.com/inference-request/input-upload"
        },
        "webhooks": {
            "base": "https://api.spotprod.segmind.com/webhook",
            "get": "https://api.spotprod.segmind.com/webhook/get",
            "add": "https://api.spotprod.segmind.com/webhook/add",
            "update": "https://api.spotprod.segmind.com/webhook/update",
            "delete": "https://api.spotprod.segmind.com/webhook/inactive",
            "logs": "https://api.spotprod.segmind.com/webhook/dispatch-logs"
        },
        "accounts": {
            "current": "https://cloud.segmind.com/api/auth/authenticate"
        },
        "generations": {
            "list": "/generations",
            "get": "/generations/{generation_id}"
        }
    }


@pytest.fixture
def response_time_scenarios():
    """Different response time scenarios for testing."""
    return {
        "fast": 0.1,      # 100ms
        "normal": 0.5,    # 500ms
        "slow": 2.0,      # 2 seconds
        "timeout": 35.0   # Above typical timeout
    }


@pytest.fixture
def content_type_variants():
    """Different content-type headers for testing."""
    return {
        "json": "application/json",
        "json_utf8": "application/json; charset=utf-8",
        "text": "text/plain",
        "html": "text/html",
        "xml": "application/xml",
        "form": "application/x-www-form-urlencoded",
        "multipart": "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW"
    }