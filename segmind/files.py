import base64
from pathlib import Path
from typing import Any, List, Union

from segmind.resource import Namespace


class Files(Namespace):
    """Client for Segmind Files/Storage API.

    Provides methods to upload files to Segmind Storage and receive
    persistent URLs that can be used across multiple model runs.
    """

    STORAGE_BASE_URL = "https://workflows-api.segmind.com"

    def upload(self, file_paths: Union[str, Path, List[Union[str, Path]]]) -> dict[str, Any]:
        """Upload one or more media files to Segmind Storage.

        Uses the Segmind Storage API to upload files as base64-encoded data URLs
        and returns persistent URLs that can be reused across model runs.

        Args:
            file_paths: Single file path or list of file paths to upload.
                       Supports images (JPEG, PNG, WebP, etc.)

        Returns:
            Dictionary containing:
                - urls: List of persistent storage URLs for the uploaded files

        Raises:
            FileNotFoundError: If any file doesn't exist
            ValueError: If any file is not a supported media format

        Example:
            >>> client = SegmindClient(api_key="...")
            >>> # Single file upload
            >>> result = client.files.upload("image.jpg")
            >>> print(result["urls"][0])
            https://storage.segmind.com/assets/...

            >>> # Batch upload
            >>> result = client.files.upload(["image1.jpg", "image2.png"])
            >>> print(result["urls"])
            ['https://storage.segmind.com/assets/...', ...]
        """
        # Normalize to list
        if isinstance(file_paths, (str, Path)):
            file_paths = [file_paths]

        data_urls = []
        for file_path in file_paths:
            file_path = Path(file_path)
            content_type = self._get_content_type(file_path)
            data_url = self._file_to_data_url(file_path, content_type)
            data_urls.append(data_url)

        url = f"{self.STORAGE_BASE_URL}/upload-asset"
        response = self._client._request(
            "POST",
            url,
            json={"data_urls": data_urls},
            headers={
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
            },
        )
        return response.json()

    def _file_to_data_url(self, file_path: Path, content_type: str) -> str:
        """Convert a file to a base64-encoded data URL.

        Args:
            file_path: Path to the file
            content_type: MIME type of the file

        Returns:
            Base64-encoded data URL string (e.g., "data:image/jpeg;base64,...")
        """
        with open(file_path, "rb") as f:
            file_content = f.read()
        base64_content = base64.b64encode(file_content).decode("utf-8")
        return f"data:{content_type};base64,{base64_content}"

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
        content_types = {
            # Image formats
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
            ".webp": "image/webp",
            ".svg": "image/svg+xml",
            ".ico": "image/x-icon",
            ".tif": "image/tiff",
            ".tiff": "image/tiff",
            ".jfif": "image/jpeg",
            ".pjp": "image/jpeg",
            ".apng": "image/apng",
            ".svgz": "image/svg+xml",
            ".heif": "image/heif",
            ".heic": "image/heic",
            ".xbm": "image/x-xbitmap",
            # Audio formats
            ".mp3": "audio/mpeg",
            ".aiff": "audio/aiff",
            ".wma": "audio/x-ms-wma",
            ".au": "audio/basic",
            # Video formats
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".mkv": "video/x-matroska",
            ".wmv": "video/x-ms-wmv",
            ".flv": "video/x-flv",
            ".webm": "video/webm",
            ".mpeg": "video/mpeg",
            ".mpg": "video/mpeg",
        }

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        if file_path.suffix.lower() not in content_types:
            raise ValueError(f"File is not a supported media format: {file_path}")

        extension = file_path.suffix.lower()

        return content_types.get(extension, "application/octet-stream")
