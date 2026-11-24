from pathlib import Path
from typing import Any, Dict, Iterator, List, Union

import httpx

from segmind.exceptions import SegmindError, raise_for_status
from segmind.resource import Namespace

# How much of a file is held in memory at once while it uploads.
_CHUNK_SIZE = 1024 * 1024


def _read_chunks(path: Path, chunk_size: int) -> Iterator[bytes]:
    """Yields a file's bytes a chunk at a time, so the whole file is never in memory."""
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                return
            yield chunk


class Files(Namespace):
    """Client for Segmind Files/Storage API.

    Provides methods to upload files to Segmind Storage and receive
    persistent URLs that can be used across multiple model runs.
    """

    # The asset library API. Uploads land in the caller's asset library.
    ASSETS_BASE_URL = "https://platform-api.segmind.com"

    def upload(self, file_paths: Union[str, Path, List[Union[str, Path]]]) -> Dict[str, Any]:
        """Upload one or more media files to your Segmind asset library.

        Each file goes straight to storage on a presigned URL, streamed from
        disk, so a large video is never held in memory. The returned URLs are
        public and do not expire.

        Args:
            file_paths: Single file path or list of file paths to upload.
                       Supports images, audio and video.

        Returns:
            Dictionary containing:
                - file_urls: List of persistent storage URLs, in the order given
                - message: Success message

        Raises:
            FileNotFoundError: If any file doesn't exist
            ValueError: If any file is not a supported media format
            SegmindError: If the asset library or storage refuses a file. Files
                earlier in the list stay uploaded.

        Example:
            >>> client = SegmindClient(api_key="...")
            >>> # Single file upload
            >>> result = client.files.upload("image.jpg")
            >>> print(result["file_urls"][0])
            https://images.segmind.com/assets/...

            >>> # Batch upload
            >>> result = client.files.upload(["image1.jpg", "image2.png"])
            >>> print(result["file_urls"])
            ['https://images.segmind.com/assets/...', ...]
        """
        # Normalize to list
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]

        # Check every file before uploading any of them.
        files = [(Path(p), self._get_content_type(Path(p))) for p in file_paths]
        file_urls = [self._upload_one(path, content_type) for path, content_type in files]
        return {"message": "Files uploaded successfully", "file_urls": file_urls}

    def _upload_one(self, path: Path, content_type: str) -> str:
        """Presign, PUT the bytes, then confirm to register the file in the asset library."""
        size = path.stat().st_size
        ticket = self._client._request(
            "POST",
            f"{self.ASSETS_BASE_URL}/upload-asset/presign",
            json={"filename": path.name, "contentType": content_type, "size": size},
        ).json()
        if not all(ticket.get(key) for key in ("presignedUrl", "s3Key", "publicUrl")):
            raise SegmindError(
                detail="the asset presign response had no presignedUrl, s3Key or publicUrl"
            )

        self._put(ticket["presignedUrl"], path, content_type, size)

        # Confirming upserts on the key, so a repeated confirm cannot register the file twice.
        confirmed = self._client._request(
            "POST",
            f"{self.ASSETS_BASE_URL}/upload-asset/confirm",
            json={
                "s3Key": ticket["s3Key"],
                "publicUrl": ticket["publicUrl"],
                "contentType": content_type,
                "filename": path.name,
            },
        ).json()
        return (confirmed.get("asset") or {}).get("url") or ticket["publicUrl"]

    def _put(self, url: str, path: Path, content_type: str, size: int) -> None:
        """Streams the file to a presigned URL.

        The URL signs Content-Type and Content-Length, so both must match the
        presign. Setting Content-Length also keeps httpx from sending the body
        chunked, which a presigned PUT refuses. A separate client sends no API
        key or SDK headers to the storage host.
        """
        timeout = httpx.Timeout(self._client.timeout, connect=5.0)
        with httpx.Client(timeout=timeout) as storage:
            response = storage.put(
                url,
                content=_read_chunks(path, _CHUNK_SIZE),
                headers={"Content-Type": content_type, "Content-Length": str(size)},
            )
        raise_for_status(response)

    # -------------------------------------------------------------------------
    # Legacy upload method (deprecated)
    # Uses the older multipart form-data API endpoint
    # -------------------------------------------------------------------------
    # def upload_legacy(self, file_path: Union[str, Path]) -> dict[str, Any]:
    #     """Upload a media file using the legacy API (deprecated).
    #
    #     This method uses the older multipart form-data upload endpoint.
    #     Consider using upload() instead which uses the newer Storage API.
    #
    #     Args:
    #         file_path: Path to the media file to upload
    #
    #     Returns:
    #         Dictionary containing the upload response
    #
    #     Raises:
    #         FileNotFoundError: If the file doesn't exist
    #         ValueError: If the file is not a supported media format
    #     """
    #     file_path = Path(file_path)
    #
    #     content_type = self._get_content_type(file_path)
    #
    #     with open(file_path, "rb") as f:
    #         files = {"file": (file_path.name, f, content_type)}
    #
    #         url = "https://api.spotprod.segmind.com/inference-request/input-upload"
    #         response = self._client._request("POST", url, files=files)
    #         return response.json()
    # -------------------------------------------------------------------------

    def _get_content_type(self, file_path: Path) -> str:
        """Check if the file is a supported media format and get the content type.

        Args:
            file_path: Path to the file

        Returns:
            Content type string if the file is a supported media format

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the path is not a file or format is not supported
        """
        # What the asset library accepts. It refuses any other type with a 400, so a
        # type added here has to be one it takes.
        content_types = {
            # Image formats
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".webp": "image/webp",
            ".avif": "image/avif",
            ".tif": "image/tiff",
            ".tiff": "image/tiff",
            ".jfif": "image/jpeg",
            ".pjp": "image/jpeg",
            # Audio formats
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".flac": "audio/flac",
            ".aac": "audio/aac",
            ".m4a": "audio/mp4",
            # Video formats
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".mkv": "video/x-matroska",
            ".wmv": "video/wmv",
            ".flv": "video/flv",
            ".webm": "video/webm",
        }

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        if file_path.suffix.lower() not in content_types:
            raise ValueError(f"File is not a supported media format: {file_path}")

        extension = file_path.suffix.lower()

        return content_types.get(extension, "application/octet-stream")
