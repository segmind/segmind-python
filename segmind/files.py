from pathlib import Path
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    from segmind.client import SegmindClient


class Files:
    """Client for Segmind Files API."""

    def __init__(self, client: "SegmindClient"):
        """Initialize Files client.

        Args:
            client: SegmindClient instance to use for API calls.
        """
        self.client = client
        self.upload_url = "https://api.spotprod.segmind.com/inference-request/input-upload"

        self.content_types = {
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

        self.check_supported_media(file_path)

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, self._get_content_type(file_path))}

            response = self.client._client.post(self.upload_url, files=files)
            response.raise_for_status()
            return response.json()

    def check_supported_media(self, file_path: Path) -> None:
        """Check if the file is a supported media format.

        Args:
            file_path: Path to the file

        Returns:
            True if the file is a supported media format
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")

        if file_path.suffix.lower() not in self.content_types:
            raise ValueError(f"File is not a supported media format: {file_path}")

    def _get_content_type(self, file_path: Path) -> str:
        """Get the content type for a media file based on its extension.

        Args:
            file_path: Path to the media file

        Returns:
            Content type string
        """
        extension = file_path.suffix.lower()

        return self.content_types.get(extension, "application/octet-stream")
