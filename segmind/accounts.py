from typing import Any, Dict

from segmind.resource import Namespace


class Accounts(Namespace):
    """Client for Segmind Accounts API."""

    def current(self) -> Dict[str, Any]:
        """Get account information.

        Returns:
            Dictionary containing the account information
        """
        url = "https://cloud.segmind.com/api/auth/authenticate"
        response = self._client._request("GET", url)
        return response.json()
