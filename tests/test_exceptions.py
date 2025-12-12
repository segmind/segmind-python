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
