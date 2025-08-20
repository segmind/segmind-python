from typing import Any

from segmind.resource import Namespace


class Accounts(Namespace):
    """Client for Segmind Accounts API."""

    def get(self) -> dict[str, Any]:
        """Get account information.

        Returns:
            Dictionary containing the account information
        """
        url = "https://cloud.segmind.com/api/auth/authenticate"
        response = self._client._request("GET", url)
        return response.json()
