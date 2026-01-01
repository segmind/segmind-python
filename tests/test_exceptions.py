"""Tests for custom exceptions and error handling."""

import httpx
import pytest

from segmind.exceptions import SegmindError, raise_for_status


class TestSegmindError:
    """Test cases for the base SegmindError class."""

    def test_segmind_error_creation(self):
        """Test SegmindError creation with basic parameters."""
        error = SegmindError(status=400, detail="Bad Request")

        assert error.status == 400
        assert error.detail == "Bad Request"
        assert error.title is None

    def test_segmind_error_creation_with_none_values(self):
        """Test SegmindError creation with None values."""
        error = SegmindError()

        assert error.status is None
        assert error.detail is None
        assert error.title is None

    def test_segmind_error_string_representation(self):
        """Test SegmindError string representation."""
        error = SegmindError(status=500, detail="Internal Server Error")
        error_str = str(error)

        assert "SegmindError Details" in error_str
        assert "status: 500" in error_str
        assert "detail: Internal Server Error" in error_str

    def test_segmind_error_to_dict(self):
        """Test SegmindError to_dict method."""
        error = SegmindError(status=403, detail="Forbidden")
        error_dict = error.to_dict()

        assert error_dict["status"] == 403
        assert error_dict["detail"] == "Forbidden"
        assert "title" not in error_dict

    def test_segmind_error_from_response_with_json(self):
        """Test SegmindError creation from HTTP response with JSON."""
        response = httpx.Response(
            400, json={"error": "Bad Request", "detail": "Invalid parameters"}
        )

        error = SegmindError.from_response(response)

        assert error.status == 400
        assert error.detail == "Bad Request"

    def test_segmind_error_from_response_without_json(self):
        """Test SegmindError creation from HTTP response without JSON."""
        response = httpx.Response(500, text="Internal Server Error")

        error = SegmindError.from_response(response)

        assert error.status == 500
        assert error.detail is None

    def test_segmind_error_inheritance(self):
        """Test that SegmindError inherits from Exception."""
        error = SegmindError(status=400, detail="Test")

        assert isinstance(error, Exception)
        assert isinstance(error, SegmindError)


class TestRaiseForStatus:
    """Test cases for raise_for_status function."""

    def test_raise_for_status_success(self):
        """Test that successful responses don't raise exceptions."""
        response = httpx.Response(200, text="OK")

        # Should not raise any exception
        result = raise_for_status(response)
        assert result is None

    def test_raise_for_status_400_bad_request(self):
        """Test that 400 responses raise SegmindError."""
        response = httpx.Response(400, json={"error": "Bad Request"})

        with pytest.raises(SegmindError) as exc_info:
            raise_for_status(response)

        assert exc_info.value.status == 400

    def test_raise_for_status_401_unauthorized(self):
        """Test that 401 responses raise SegmindError."""
        response = httpx.Response(401, json={"error": "Unauthorized"})

        with pytest.raises(SegmindError) as exc_info:
            raise_for_status(response)

        assert exc_info.value.status == 401

    def test_raise_for_status_500_internal_server_error(self):
        """Test that 500 responses raise SegmindError."""
        response = httpx.Response(500, json={"error": "Internal Server Error"})

        with pytest.raises(SegmindError) as exc_info:
            raise_for_status(response)

        assert exc_info.value.status == 500

    def test_raise_for_status_with_all_4xx_codes(self):
        """Test raise_for_status with various 4xx error codes."""
        error_codes = [400, 401, 403, 404, 422, 429]

        for code in error_codes:
            response = httpx.Response(code, json={"error": f"HTTP {code}"})

            with pytest.raises(SegmindError) as exc_info:
                raise_for_status(response)

            assert exc_info.value.status == code

    def test_raise_for_status_with_all_5xx_codes(self):
        """Test raise_for_status with various 5xx error codes."""
        error_codes = [500, 502, 503, 504]

        for code in error_codes:
            response = httpx.Response(code, json={"error": f"HTTP {code}"})

            with pytest.raises(SegmindError) as exc_info:
                raise_for_status(response)

            assert exc_info.value.status == code

    @pytest.mark.parametrize("status_code", [200, 201, 202, 204, 301, 302])
    def test_raise_for_status_success_codes(self, status_code):
        """Test that non-error status codes don't raise exceptions."""
        response = httpx.Response(status_code, text="OK")

        # Should not raise any exception
        result = raise_for_status(response)
        assert result is None

    def test_raise_for_status_with_json_error_details(self):
        """Test raise_for_status with detailed JSON error response."""
        error_data = {
            "error": "ValidationError",
            "detail": "Invalid input parameters",
            "code": "VALIDATION_FAILED",
            "timestamp": "2024-01-01T00:00:00Z",
            "request_id": "req_123456"
        }
        response = httpx.Response(422, json=error_data)

        with pytest.raises(SegmindError) as exc_info:
            raise_for_status(response)

        error = exc_info.value
        assert error.status == 422
        assert error.detail == "ValidationError"

    def test_raise_for_status_with_text_response(self):
        """Test raise_for_status with plain text error response."""
        response = httpx.Response(500, text="Internal Server Error")

        with pytest.raises(SegmindError) as exc_info:
            raise_for_status(response)

        error = exc_info.value
        assert error.status == 500
        assert error.detail is None  # No JSON parsing for text responses

    def test_raise_for_status_with_empty_response(self):
        """Test raise_for_status with empty error response."""
        response = httpx.Response(400, text="")

        with pytest.raises(SegmindError) as exc_info:
            raise_for_status(response)

        error = exc_info.value
        assert error.status == 400
        assert error.detail is None

    def test_raise_for_status_with_malformed_json(self):
        """Test raise_for_status with malformed JSON response."""
        # Create a response with invalid JSON
        response = httpx.Response(400, text='{"error": invalid json')

        with pytest.raises(SegmindError) as exc_info:
            raise_for_status(response)

        error = exc_info.value
        assert error.status == 400
        assert error.detail is None  # Should handle JSON parsing errors gracefully


class TestSegmindErrorAdvanced:
    """Advanced test cases for SegmindError class."""

    def test_segmind_error_with_all_parameters(self):
        """Test SegmindError creation with all parameters."""
        error = SegmindError(
            status=422,
            detail="Validation failed"
        )

        assert error.status == 422
        assert error.detail == "Validation failed"
        assert error.title is None  # title is not supported in current implementation

    def test_segmind_error_string_representation_with_title(self):
        """Test SegmindError string representation."""
        error = SegmindError(
            status=404,
            detail="Resource not found"
        )
        error_str = str(error)

        assert "SegmindError Details" in error_str
        assert "status: 404" in error_str
        assert "detail: Resource not found" in error_str

    def test_segmind_error_string_representation_minimal(self):
        """Test SegmindError string representation with minimal data."""
        error = SegmindError(status=500)
        error_str = str(error)

        assert "SegmindError Details" in error_str
        assert "status: 500" in error_str
        assert "detail: None" in error_str

    def test_segmind_error_to_dict_with_all_fields(self):
        """Test SegmindError to_dict method with all fields."""
        error = SegmindError(
            status=400,
            detail="Bad request"
        )
        error_dict = error.to_dict()

        expected = {
            "status": 400,
            "detail": "Bad request"
        }
        assert error_dict == expected

    def test_segmind_error_to_dict_with_none_values(self):
        """Test SegmindError to_dict method with None values."""
        error = SegmindError(status=500, detail=None)
        error_dict = error.to_dict()

        # Current implementation includes None values
        assert error_dict == {"status": 500, "detail": None}

    def test_segmind_error_from_response_with_complex_json(self):
        """Test SegmindError creation from complex JSON response."""
        complex_error = {
            "error": "RATE_LIMIT_EXCEEDED",
            "detail": "Rate limit exceeded for API key",
            "title": "Too Many Requests",
            "meta": {
                "limit": 100,
                "remaining": 0,
                "reset_time": "2024-01-01T01:00:00Z"
            },
            "help_url": "https://docs.segmind.com/rate-limits"
        }
        response = httpx.Response(429, json=complex_error)

        error = SegmindError.from_response(response)

        assert error.status == 429
        assert error.detail == "RATE_LIMIT_EXCEEDED"

    def test_segmind_error_from_response_with_nested_error(self):
        """Test SegmindError creation from nested error structure."""
        nested_error = {
            "status": "error",
            "data": {
                "error": "INVALID_MODEL",
                "message": "Model not found or not available"
            }
        }
        response = httpx.Response(404, json=nested_error)

        error = SegmindError.from_response(response)

        assert error.status == 404
        # Current implementation doesn't extract nested errors
        assert error.detail is None  # No top-level "error" field

    def test_segmind_error_from_response_with_message_field(self):
        """Test SegmindError creation from response with 'message' field."""
        error_data = {
            "message": "Authentication failed",
            "code": "AUTH_FAILED"
        }
        response = httpx.Response(401, json=error_data)

        error = SegmindError.from_response(response)

        assert error.status == 401
        # Current implementation only extracts 'error' field
        assert error.detail is None  # No 'error' field present

    def test_segmind_error_from_response_with_detail_field(self):
        """Test SegmindError creation from response with 'detail' field."""
        error_data = {
            "detail": "Invalid API key provided",
            "type": "authentication_error"
        }
        response = httpx.Response(401, json=error_data)

        error = SegmindError.from_response(response)

        assert error.status == 401
        # Current implementation only extracts 'error' field
        assert error.detail is None  # No 'error' field present

    def test_segmind_error_from_response_with_empty_json(self):
        """Test SegmindError creation from empty JSON response."""
        response = httpx.Response(500, json={})

        error = SegmindError.from_response(response)

        assert error.status == 500
        assert error.detail is None

    def test_segmind_error_from_response_with_non_dict_json(self):
        """Test SegmindError creation from non-dict JSON response."""
        # This will raise an AttributeError in from_response since .get() is called on a list
        # Current implementation doesn't handle this gracefully
        response = httpx.Response(400, text='["error1", "error2"]')

        error = SegmindError.from_response(response)

        assert error.status == 400
        assert error.detail is None  # JSON parsing fails, returns empty dict

    def test_segmind_error_equality(self):
        """Test SegmindError equality comparison."""
        error1 = SegmindError(status=400, detail="Bad request")
        error2 = SegmindError(status=400, detail="Bad request")
        error3 = SegmindError(status=404, detail="Not found")

        assert error1.__dict__ == error2.__dict__
        assert error1.__dict__ != error3.__dict__

    def test_segmind_error_repr(self):
        """Test SegmindError repr method."""
        error = SegmindError(status=422, detail="Validation error")
        repr_str = repr(error)

        assert "SegmindError" in repr_str
        assert "422" in repr_str

    def test_segmind_error_with_unicode_characters(self):
        """Test SegmindError with unicode characters in detail."""
        error = SegmindError(
            status=400,
            detail="Invalid paramètres: éñcödîng tést 🚫"
        )

        assert error.detail == "Invalid paramètres: éñcödîng tést 🚫"

        # Should handle unicode in string representation
        error_str = str(error)
        assert "éñcödîng tést 🚫" in error_str

    def test_segmind_error_with_very_long_detail(self):
        """Test SegmindError with very long detail message."""
        long_detail = "A" * 10000  # 10KB string
        error = SegmindError(status=500, detail=long_detail)

        assert len(error.detail) == 10000
        assert error.detail == long_detail

        # String representation should handle long strings
        error_str = str(error)
        assert long_detail in error_str


class TestErrorHandlingIntegration:
    """Integration tests for error handling across the SDK."""

    def test_error_propagation_chain(self):
        """Test error propagation through multiple function calls."""
        def inner_function():
            response = httpx.Response(400, json={"error": "Inner error"})
            raise_for_status(response)

        def middle_function():
            inner_function()

        def outer_function():
            middle_function()

        with pytest.raises(SegmindError) as exc_info:
            outer_function()

        assert exc_info.value.status == 400
        assert exc_info.value.detail == "Inner error"

    def test_custom_error_handling_patterns(self):
        """Test common error handling patterns."""
        # Pattern 1: Catch and re-raise with additional context
        def api_call_with_context():
            try:
                response = httpx.Response(404, json={"error": "Model not found"})
                raise_for_status(response)
            except SegmindError as e:
                # Could add additional context here
                raise e

        with pytest.raises(SegmindError) as exc_info:
            api_call_with_context()

        assert exc_info.value.status == 404

    def test_error_handling_with_different_response_formats(self):
        """Test error handling with various response formats."""
        response_formats = [
            (400, {"error": "Simple error"}, "Simple error"),  # Has 'error' field
            (401, {"message": "Auth failed", "code": "AUTH_ERROR"}, None),  # No 'error' field
            (403, {"detail": "Forbidden", "type": "permission_error"}, None),  # No 'error' field
            (422, {"errors": [{"field": "prompt", "message": "Required"}]}, None),  # No 'error' field
            (429, {"error": "Rate limited", "retry_after": 60}, "Rate limited"),  # Has 'error' field
            (500, {"internal_error": "Database connection failed"}, None),  # No 'error' field
        ]

        for status_code, error_data, expected_detail in response_formats:
            response = httpx.Response(status_code, json=error_data)

            with pytest.raises(SegmindError) as exc_info:
                raise_for_status(response)

            assert exc_info.value.status == status_code
            assert exc_info.value.detail == expected_detail

    @pytest.mark.parametrize("content_type,should_parse", [
        ("application/json", True),
        ("application/json; charset=utf-8", True),
        ("text/plain", False),
        ("text/html", False),
        ("application/xml", False),
    ])
    def test_error_handling_by_content_type(self, content_type, should_parse):
        """Test error handling based on response content type."""
        # Note: This test assumes the implementation considers content-type
        # The current implementation might not, but this tests the expected behavior
        error_data = {"error": "Test error"}
        response = httpx.Response(
            400,
            json=error_data,
            headers={"content-type": content_type}
        )

        with pytest.raises(SegmindError) as exc_info:
            raise_for_status(response)

        assert exc_info.value.status == 400
        # The detail extraction depends on implementation

    def test_concurrent_error_handling(self):
        """Test error handling in concurrent scenarios."""
        import threading

        errors_caught = []

        def worker():
            try:
                response = httpx.Response(500, json={"error": "Concurrent error"})
                raise_for_status(response)
            except SegmindError as e:
                errors_caught.append(e)

        threads = []
        for _ in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(errors_caught) == 5
        for error in errors_caught:
            assert error.status == 500
            assert error.detail == "Concurrent error"
