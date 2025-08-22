from typing import Any

from segmind.resource import Namespace


class Models(Namespace):
    """Client for Segmind Models API."""

    def list(self) -> dict[str, Any]:
        """Get all available models.

        Returns:
            Dictionary containing the models list response
        """
        url = "https://api.spotprod.segmind.com/inference-model-information/list"
        response = self._client._request("GET", url)
        return response.json()
