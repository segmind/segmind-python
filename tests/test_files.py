"""Comprehensive tests for the Files module."""

import tempfile
from pathlib import Path
from unittest import mock

import pytest
import httpx

from segmind.files import Files


class TestFiles:
    """Test cases for the Files class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock client for testing."""
        client = mock.MagicMock()
        client._request = mock.MagicMock()
        return client

    @pytest.fixture
    def files(self, mock_client):
        """Create a Files instance with mock client."""
        f = Files(client=mock_client)
        f._client = mock_client
        return f

    @pytest.fixture
    def temp_image_file(self):
        """Create a temporary image file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82')
            temp_path = Path(f.name)
        yield temp_path
        temp_path.unlink(missing_ok=True)

    @pytest.fixture
    def temp_audio_file(self):
        """Create a temporary audio file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            # Minimal MP3 header
            f.write(b'\xff\xfb\x90\x00\x00\x03\x48\x00\x00\x00\x00')
            temp_path = Path(f.name)
        yield temp_path
        temp_path.unlink(missing_ok=True)

    @pytest.fixture
    def temp_video_file(self):
        """Create a temporary video file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as f:
            # Minimal MP4 header
            f.write(b'\x00\x00\x00\x20ftypmp41\x00\x00\x00\x00mp41isom')
            temp_path = Path(f.name)
        yield temp_path
        temp_path.unlink(missing_ok=True)

    @pytest.fixture
    def sample_upload_response(self):
        """Sample upload response for testing."""
        return {
            "status": "success",
            "file_id": "file_123456",
            "filename": "test_image.png",
            "url": "https://cdn.segmind.com/files/file_123456",
            "size": 1024,
            "content_type": "image/png",
            "uploaded_at": "2024-01-01T00:00:00Z"
        }

    # ==================== Test upload() method ====================

    def test_upload_image_success(self, files, mock_client, temp_image_file, sample_upload_response):
        """Test successful image upload."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_upload_response
        mock_client._request.return_value = mock_response

        result = files.upload(temp_image_file)

        assert result["status"] == "success"
        assert result["file_id"] == "file_123456"
        assert result["content_type"] == "image/png"

        # Verify the request was made correctly with new API
        mock_client._request.assert_called_once_with(
            "POST",
            "https://workflows-api.segmind.com/upload-asset",
            json=mock.ANY,
            headers={
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json"
            }
        )

        # Check that json parameter with data_urls was passed
        call_args = mock_client._request.call_args
        assert "json" in call_args[1]
        assert "data_urls" in call_args[1]["json"]
        # Check it's a base64-encoded data URL
        assert call_args[1]["json"]["data_urls"][0].startswith("data:image/png;base64,")

    def test_upload_audio_success(self, files, mock_client, temp_audio_file):
        """Test successful audio file upload."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "file_id": "audio_123",
            "content_type": "audio/mpeg"
        }
        mock_client._request.return_value = mock_response

        result = files.upload(temp_audio_file)

        assert result["status"] == "success"
        assert result["file_id"] == "audio_123"
        assert result["content_type"] == "audio/mpeg"

    def test_upload_video_success(self, files, mock_client, temp_video_file):
        """Test successful video file upload."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = {
            "status": "success",
            "file_id": "video_456",
            "content_type": "video/mp4"
        }
        mock_client._request.return_value = mock_response

        result = files.upload(temp_video_file)

        assert result["status"] == "success"
        assert result["file_id"] == "video_456"

    def test_upload_with_string_path(self, files, mock_client, temp_image_file, sample_upload_response):
        """Test upload with string file path."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_upload_response
        mock_client._request.return_value = mock_response

        result = files.upload(str(temp_image_file))

        assert result["status"] == "success"
        mock_client._request.assert_called_once()

    def test_upload_with_pathlib_path(self, files, mock_client, temp_image_file, sample_upload_response):
        """Test upload with pathlib.Path object."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_upload_response
        mock_client._request.return_value = mock_response

        result = files.upload(temp_image_file)

        assert result["status"] == "success"
        mock_client._request.assert_called_once()

    def test_upload_file_not_found(self, files):
        """Test upload with non-existent file."""
        non_existent_path = Path("/path/that/does/not/exist.png")
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            files.upload(non_existent_path)

    def test_upload_directory_instead_of_file(self, files):
        """Test upload with directory path instead of file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            
            with pytest.raises(ValueError, match="Path is not a file"):
                files.upload(dir_path)

    def test_upload_unsupported_file_format(self, files):
        """Test upload with unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"This is a text file")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="File is not a supported media format"):
                files.upload(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_upload_network_error(self, files, mock_client, temp_image_file):
        """Test upload with network error."""
        mock_client._request.side_effect = httpx.NetworkError("Connection failed")

        with pytest.raises(httpx.NetworkError):
            files.upload(temp_image_file)

    def test_upload_api_error(self, files, mock_client, temp_image_file):
        """Test upload with API error response."""
        mock_client._request.side_effect = httpx.HTTPStatusError(
            "Upload failed", 
            request=mock.MagicMock(),
            response=mock.MagicMock(status_code=413)  # Payload too large
        )

        with pytest.raises(httpx.HTTPStatusError):
            files.upload(temp_image_file)

    def test_upload_large_file(self, files, mock_client, sample_upload_response):
        """Test upload of a large file."""
        # Create a larger temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            large_data = b'\x89PNG\r\n\x1a\n' + b'\x00' * 10000  # 10KB of data
            f.write(large_data)
            temp_path = Path(f.name)

        try:
            mock_response = mock.MagicMock()
            mock_response.json.return_value = {
                **sample_upload_response,
                "size": 10008
            }
            mock_client._request.return_value = mock_response

            result = files.upload(temp_path)

            assert result["size"] == 10008
            mock_client._request.assert_called_once()
        finally:
            temp_path.unlink(missing_ok=True)

    # ==================== Test _get_content_type() method ====================

    @pytest.mark.parametrize("extension,expected_content_type", [
        # Image formats
        (".png", "image/png"),
        (".jpg", "image/jpeg"),
        (".jpeg", "image/jpeg"),
        (".gif", "image/gif"),
        (".bmp", "image/bmp"),
        (".webp", "image/webp"),
        (".svg", "image/svg+xml"),
        (".ico", "image/x-icon"),
        (".tif", "image/tiff"),
        (".tiff", "image/tiff"),
        (".jfif", "image/jpeg"),
        (".pjp", "image/jpeg"),
        (".apng", "image/apng"),
        (".svgz", "image/svg+xml"),
        (".heif", "image/heif"),
        (".heic", "image/heic"),
        (".xbm", "image/x-xbitmap"),
        # Audio formats
        (".mp3", "audio/mpeg"),
        (".aiff", "audio/aiff"),
        (".wma", "audio/x-ms-wma"),
        (".au", "audio/basic"),
        # Video formats
        (".mp4", "video/mp4"),
        (".avi", "video/x-msvideo"),
        (".mov", "video/quicktime"),
        (".mkv", "video/x-matroska"),
        (".wmv", "video/x-ms-wmv"),
        (".flv", "video/x-flv"),
        (".webm", "video/webm"),
        (".mpeg", "video/mpeg"),
        (".mpg", "video/mpeg"),
    ])
    def test_get_content_type_supported_formats(self, files, extension, expected_content_type):
        """Test _get_content_type with all supported file formats."""
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as f:
            f.write(b"test content")
            temp_path = Path(f.name)

        try:
            content_type = files._get_content_type(temp_path)
            assert content_type == expected_content_type
        finally:
            temp_path.unlink(missing_ok=True)

    def test_get_content_type_case_insensitive(self, files):
        """Test that file extension matching is case insensitive."""
        extensions_to_test = [".PNG", ".JPG", ".MP4", ".Mp3", ".WeBp"]
        
        for ext in extensions_to_test:
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                f.write(b"test content")
                temp_path = Path(f.name)

            try:
                content_type = files._get_content_type(temp_path)
                assert content_type is not None
                assert content_type != "application/octet-stream"
            finally:
                temp_path.unlink(missing_ok=True)

    def test_get_content_type_nonexistent_file(self, files):
        """Test _get_content_type with non-existent file."""
        non_existent_path = Path("/path/that/does/not/exist.png")
        
        with pytest.raises(FileNotFoundError, match="File not found"):
            files._get_content_type(non_existent_path)

    def test_get_content_type_directory(self, files):
        """Test _get_content_type with directory path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            dir_path = Path(temp_dir)
            
            with pytest.raises(ValueError, match="Path is not a file"):
                files._get_content_type(dir_path)

    def test_get_content_type_unsupported_format(self, files):
        """Test _get_content_type with unsupported file format."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"text content")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="File is not a supported media format"):
                files._get_content_type(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_get_content_type_no_extension(self, files):
        """Test _get_content_type with file having no extension."""
        with tempfile.NamedTemporaryFile(suffix='', delete=False) as f:
            f.write(b"content")
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="File is not a supported media format"):
                files._get_content_type(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    # ==================== Integration Tests ====================

    def test_upload_file_with_special_characters_in_name(self, files, mock_client, sample_upload_response):
        """Test upload with special characters in filename."""
        with tempfile.NamedTemporaryFile(suffix='.png', prefix='file with spaces & symbols!', delete=False) as f:
            f.write(b'\x89PNG\r\n\x1a\n')
            temp_path = Path(f.name)

        try:
            mock_response = mock.MagicMock()
            mock_response.json.return_value = sample_upload_response
            mock_client._request.return_value = mock_response

            result = files.upload(temp_path)

            assert result["status"] == "success"

            # Verify the request was made with new API (base64 encoding)
            call_args = mock_client._request.call_args
            assert "json" in call_args[1]
            assert "data_urls" in call_args[1]["json"]
            # Should still process files with special characters in name
            assert len(call_args[1]["json"]["data_urls"]) == 1
        finally:
            temp_path.unlink(missing_ok=True)

    def test_upload_file_content_verification(self, files, mock_client, sample_upload_response):
        """Test that file content is read correctly during upload."""
        test_content = b"test image content"
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(test_content)
            temp_path = Path(f.name)

        try:
            mock_response = mock.MagicMock()
            mock_response.json.return_value = sample_upload_response
            mock_client._request.return_value = mock_response

            # Mock the file reading to verify content
            with mock.patch('builtins.open', mock.mock_open(read_data=test_content)) as mock_file:
                result = files.upload(temp_path)

            assert result["status"] == "success"
            mock_file.assert_called_once_with(temp_path, "rb")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_upload_multiple_files_sequentially(self, files, mock_client):
        """Test uploading multiple files in sequence."""
        # Create multiple test files
        files_to_test = []
        for i, ext in enumerate(['.png', '.jpg', '.mp3']):
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
                f.write(b"test content " + str(i).encode())
                files_to_test.append(Path(f.name))

        try:
            # Mock responses for each upload
            mock_responses = []
            for i, file_path in enumerate(files_to_test):
                mock_resp = mock.MagicMock()
                mock_resp.json.return_value = {
                    "status": "success",
                    "file_id": f"file_{i}",
                    "filename": file_path.name
                }
                mock_responses.append(mock_resp)

            mock_client._request.side_effect = mock_responses

            # Upload all files
            results = []
            for file_path in files_to_test:
                result = files.upload(file_path)
                results.append(result)

            # Verify all uploads succeeded
            for i, result in enumerate(results):
                assert result["status"] == "success"
                assert result["file_id"] == f"file_{i}"

            assert mock_client._request.call_count == 3
        finally:
            for file_path in files_to_test:
                file_path.unlink(missing_ok=True)

    def test_upload_response_json_parsing_error(self, files, mock_client, temp_image_file):
        """Test handling of JSON parsing errors in upload response."""
        mock_response = mock.MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON response")
        mock_client._request.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid JSON response"):
            files.upload(temp_image_file)

    def test_upload_with_empty_file(self, files, mock_client):
        """Test upload with empty file."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            # Write no content, creating an empty file
            temp_path = Path(f.name)

        try:
            mock_response = mock.MagicMock()
            mock_response.json.return_value = {
                "status": "success",
                "file_id": "empty_file",
                "size": 0
            }
            mock_client._request.return_value = mock_response

            result = files.upload(temp_path)

            assert result["status"] == "success"
            assert result["size"] == 0
        finally:
            temp_path.unlink(missing_ok=True)

    # ==================== Error Handling Edge Cases ====================

    def test_upload_with_permission_error(self, files):
        """Test upload when file cannot be read due to permissions."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(b"content")
            temp_path = Path(f.name)

        try:
            # Mock permission error during file opening
            with mock.patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with pytest.raises(PermissionError):
                    files.upload(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_upload_api_url_construction(self, files, mock_client, temp_image_file, sample_upload_response):
        """Test that the correct API URL is used for upload."""
        mock_response = mock.MagicMock()
        mock_response.json.return_value = sample_upload_response
        mock_client._request.return_value = mock_response

        files.upload(temp_image_file)

        # Verify new API endpoint is used
        mock_client._request.assert_called_once_with(
            "POST",
            "https://workflows-api.segmind.com/upload-asset",
            json=mock.ANY,
            headers={
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json"
            }
        )

    @pytest.mark.parametrize("file_size", [1, 100, 1000, 10000])
    def test_upload_various_file_sizes(self, files, mock_client, sample_upload_response, file_size):
        """Test upload with various file sizes."""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            f.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * file_size)
            temp_path = Path(f.name)

        try:
            mock_response = mock.MagicMock()
            mock_response.json.return_value = {
                **sample_upload_response,
                "size": file_size + 8  # PNG header + data
            }
            mock_client._request.return_value = mock_response

            result = files.upload(temp_path)

            assert result["status"] == "success"
            assert result["size"] == file_size + 8
        finally:
            temp_path.unlink(missing_ok=True)