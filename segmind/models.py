from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from segmind.client import SegmindClient


class Models:
    """Client for Segmind Models API."""

    def __init__(self, client: "SegmindClient"):
        """Initialize Models client.

        Args:
            client: SegmindClient instance to use for API calls.
        """
        self.client = client
        self.list_url = "https://api.spotprod.segmind.com/inference-model-information/list"

    def get(self) -> dict[str, Any]:
        """Get all available models.

        Returns:
            Dictionary containing the models list response
        """
        response = self.client._client.get(self.list_url)
        response.raise_for_status()
        return response.json()
