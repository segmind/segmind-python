from pathlib import Path
from typing import Any, Union

from segmind.resource import Namespace


class Files(Namespace):
    """Client for Segmind Files API."""

    def upload(self, file_path: Union[str, Path]) -> dict[str, Any]:
        """Upload a media file (image, audio, or video).

        Args:
            file_path: Path to the media file to upload

        Returns:
            Dictionary containing the upload response

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not a supported media format
        """
        file_path = Path(file_path)

        content_type = self._get_content_type(file_path)

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, content_type)}

            url = "https://api.spotprod.segmind.com/inference-request/input-upload"
            response = self._client._request("POST", url, files=files)
            return response.json()

    def _get_content_type(self, file_path: Path) -> str:
        """Check if the file is a supported media format and get the content type.

        Args:
            file_path: Path to the file

        Returns:
            Content type string if the file is a supported media format
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
