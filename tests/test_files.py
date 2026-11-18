"""Comprehensive tests for the Files module."""

import json
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

import httpx
import pytest
import respx

from segmind.client import SegmindClient
from segmind.exceptions import SegmindError
from segmind.files import Files

# `segmind.files` the attribute is the module-level namespace; this is the module.
files_module = sys.modules["segmind.files"]


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

    # ==================== Test upload() method ====================

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


ASSETS = "https://platform-api.segmind.com"
PNG = b"\x89PNG\r\n\x1a\n\x01\x02\x03"


def asset_ticket(filename):
    """`POST /upload-asset/presign` on the asset library, as production returns it."""
    key = f"assets/u1@test.dev/0f3a-{filename}"
    return {
        "presignedUrl": f"https://segmind-nodes-assets.s3.us-east-1.amazonaws.com/{key}"
        "?X-Amz-SignedHeaders=content-length%3Bcontent-type%3Bhost&X-Amz-Signature=sig",
        "s3Key": key,
        "publicUrl": f"https://images.segmind.com/{key}",
        "filename": filename,
        "contentType": "image/png",
        "size": 11,
        "tags": [],
    }


def write(tmp_path, name, content):
    path = tmp_path / name
    path.write_bytes(content)
    return path


class TestUploadToAssetLibrary:
    """`files.upload` presigns, streams the file to storage, then confirms it."""

    @pytest.fixture
    def client(self):
        return SegmindClient(api_key="sk-test")

    @pytest.fixture
    def router(self):
        with respx.mock(assert_all_called=False) as router:
            yield router

    def mock_upload(self, router, filename, asset_url=None, put_status=200):
        """Routes one presign, PUT and confirm; returns what the PUT carried."""
        ticket = asset_ticket(filename)
        sent = {}

        def on_put(request):
            sent["headers"] = request.headers
            sent["body"] = request.read()
            return httpx.Response(put_status, text="" if put_status == 200 else "<Error>Denied</Error>")

        router.post(f"{ASSETS}/upload-asset/presign", json__filename=filename).mock(
            return_value=httpx.Response(200, json=ticket)
        )
        router.put(ticket["presignedUrl"]).mock(side_effect=on_put)
        router.post(f"{ASSETS}/upload-asset/confirm", json__filename=filename).mock(
            return_value=httpx.Response(200, json={"asset": {"url": asset_url or ticket["publicUrl"]}})
        )
        return ticket, sent

    def test_presigns_streams_and_confirms(self, client, router, tmp_path):
        path = write(tmp_path, "logo.png", PNG)
        ticket, sent = self.mock_upload(router, "logo.png")

        result = client.files.upload(path)

        assert result == {"message": "Files uploaded successfully", "file_urls": [ticket["publicUrl"]]}
        presign, put, confirm = router.calls
        assert json.loads(presign.request.content) == {"filename": "logo.png", "contentType": "image/png", "size": 11}
        assert presign.request.headers["x-api-key"] == "sk-test"
        assert put.request.method == "PUT"
        assert sent["body"] == PNG
        assert sent["headers"]["content-type"] == "image/png"
        assert sent["headers"]["content-length"] == "11"
        assert "transfer-encoding" not in sent["headers"]
        assert json.loads(confirm.request.content) == {
            "s3Key": ticket["s3Key"],
            "publicUrl": ticket["publicUrl"],
            "contentType": "image/png",
            "filename": "logo.png",
        }
        assert confirm.request.headers["x-api-key"] == "sk-test"

    def test_never_sends_the_key_or_sdk_headers_to_storage(self, client, router, tmp_path):
        path = write(tmp_path, "logo.png", PNG)
        _, sent = self.mock_upload(router, "logo.png")
        client.files.upload(path)
        assert "x-api-key" not in sent["headers"]
        assert "x-initiator" not in sent["headers"]
        assert "segmind" not in sent["headers"].get("user-agent", "")

    def test_reads_the_file_a_chunk_at_a_time(self, client, router, tmp_path, monkeypatch):
        content = bytes(range(10)) * 3
        path = write(tmp_path, "clip.mp4", content)
        _, sent = self.mock_upload(router, "clip.mp4")
        chunks = []
        read_chunks = files_module._read_chunks

        def spy(p, size):
            for chunk in read_chunks(p, size):
                chunks.append(chunk)
                yield chunk

        monkeypatch.setattr(files_module, "_CHUNK_SIZE", 8)
        monkeypatch.setattr(files_module, "_read_chunks", spy)
        client.files.upload(path)

        assert [len(c) for c in chunks] == [8, 8, 8, 6]
        assert sent["body"] == content
        assert sent["headers"]["content-length"] == "30"

    def test_returns_the_confirmed_url(self, client, router, tmp_path):
        path = write(tmp_path, "logo.png", PNG)
        self.mock_upload(router, "logo.png", asset_url="https://images.segmind.com/assets/u1/renamed.png")
        assert client.files.upload(path)["file_urls"] == ["https://images.segmind.com/assets/u1/renamed.png"]

    def test_uploads_a_list_in_order(self, client, router, tmp_path):
        first = write(tmp_path, "a.png", PNG)
        second = write(tmp_path, "b.mp3", b"\xff\xfb\x90\x00")
        a, _ = self.mock_upload(router, "a.png")
        b, _ = self.mock_upload(router, "b.mp3")

        result = client.files.upload([str(first), second])

        assert result["file_urls"] == [a["publicUrl"], b["publicUrl"]]
        presigns = [json.loads(c.request.content) for c in router.calls if c.request.url.path.endswith("presign")]
        assert presigns == [
            {"filename": "a.png", "contentType": "image/png", "size": 11},
            {"filename": "b.mp3", "contentType": "audio/mpeg", "size": 4},
        ]

    def test_checks_every_file_before_uploading_any(self, client, router, tmp_path):
        good = write(tmp_path, "a.png", PNG)
        bad = write(tmp_path, "notes.txt", b"hello")
        with pytest.raises(ValueError, match="not a supported media format"):
            client.files.upload([good, bad])
        assert router.calls.call_count == 0

    def test_a_refused_put_raises_and_is_not_confirmed(self, client, router, tmp_path):
        path = write(tmp_path, "logo.png", PNG)
        self.mock_upload(router, "logo.png", put_status=403)
        with pytest.raises(SegmindError) as raised:
            client.files.upload(path)
        assert raised.value.status == 403
        assert not any(c.request.url.path.endswith("confirm") for c in router.calls)

    def test_a_refused_presign_raises_before_any_put(self, client, router, tmp_path):
        path = write(tmp_path, "logo.png", PNG)
        router.post(f"{ASSETS}/upload-asset/presign").mock(
            return_value=httpx.Response(400, json={"error": "File type not allowed: image/png"})
        )
        with pytest.raises(SegmindError) as raised:
            client.files.upload(path)
        assert raised.value.status == 400
        assert router.calls.call_count == 1

    def test_an_incomplete_ticket_raises(self, client, router, tmp_path):
        path = write(tmp_path, "logo.png", PNG)
        router.post(f"{ASSETS}/upload-asset/presign").mock(return_value=httpx.Response(200, json={"s3Key": "k"}))
        with pytest.raises(SegmindError, match="presignedUrl"):
            client.files.upload(path)
        assert router.calls.call_count == 1


class TestUploadOverTheWire:
    """A real httpx client against a local server: the body arrives whole, not chunked."""

    def test_streams_a_file_with_its_exact_length(self, tmp_path, monkeypatch):
        content = bytes(i % 251 for i in range(3 * 1024 * 1024 + 17))
        path = write(tmp_path, "clip.mp4", content)
        received = {}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):  # noqa: N802 (http.server names the handler)
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                if self.path == "/upload-asset/presign":
                    received["presign"] = body
                    reply = {"presignedUrl": f"{origin}/put/clip.mp4", "s3Key": "assets/u1/clip.mp4",
                             "publicUrl": "https://images.test/assets/u1/clip.mp4"}
                else:
                    reply = {"asset": {"url": "https://images.test/assets/u1/clip.mp4"}}
                data = json.dumps(reply).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_PUT(self):  # noqa: N802 (http.server names the handler)
                received["put_headers"] = dict(self.headers)
                received["put_body"] = self.rfile.read(int(self.headers["Content-Length"]))
                self.send_response(200)
                self.send_header("Content-Length", "0")
                self.end_headers()

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        origin = f"http://127.0.0.1:{server.server_address[1]}"
        threading.Thread(target=server.serve_forever, daemon=True).start()
        monkeypatch.setattr(Files, "ASSETS_BASE_URL", origin)
        try:
            result = SegmindClient(api_key="sk-test").files.upload(path)
        finally:
            server.shutdown()
            server.server_close()

        assert result["file_urls"] == ["https://images.test/assets/u1/clip.mp4"]
        assert received["presign"] == {"filename": "clip.mp4", "contentType": "video/mp4", "size": len(content)}
        assert received["put_headers"]["Content-Length"] == str(len(content))
        assert "Transfer-Encoding" not in received["put_headers"]
        assert received["put_body"] == content
