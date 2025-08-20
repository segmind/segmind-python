from typing import Any, Optional

from segmind.resource import Namespace


class Generations(Namespace):
    """Client for Segmind Generations API."""

    def recent(self, model_name: str) -> dict[str, Any]:
        """Get recent generations for a model.

        Args:
            model_name: Name of the model to get recent generations for (required)

        Returns:
            Dictionary containing recent generations response
        """
        params = {"model_name": model_name}
        url = "https://api.spotprod.segmind.com/inference-request/recent-generations"
        response = self._client._request("GET", url, params=params)
        return response.json()

    def list(
        self,
        page: int = 1,
        model_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> dict[str, Any]:
        """Get generations with pagination and filtering.

        Args:
            page: Page number for pagination (default: 1)
            model_name: Name of the model to filter by (optional)
            start_date: Start date filter in YYYY-MM-DD format (optional)
            end_date: End date filter in YYYY-MM-DD format (optional)

        Returns:
            Dictionary containing generations list response
        """
        params = {"page": page}

        if model_name:
            params["model_name"] = model_name
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        url = "https://api.spotprod.segmind.com/inference-request/generations"
        response = self._client._request("GET", url, params=params)
        return response.json()
