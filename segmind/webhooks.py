from typing import Any, Optional

from segmind.resource import Namespace


class Webhooks(Namespace):
    """Client for Segmind Webhooks API."""

    base_url = "https://api.spotprod.segmind.com/webhook"

    def get(self) -> dict[str, Any]:
        """Get all webhooks.

        Returns:
            Dictionary containing the webhooks response
        """
        url = f"{self.base_url}/get"

        response = self._client._request("GET", url)
        return response.json()

    def add(self, webhook_url: str, event_types: list[str]) -> dict[str, Any]:
        """Add a new webhook.

        Args:
            webhook_url: The URL to send webhook notifications to
            event_types: List of event types to subscribe to (default: ["PIXELFLOW"])

        Returns:
            Dictionary containing the add webhook response
        """
        url = f"{self.base_url}/add"

        if not event_types:
            raise ValueError("Event types must be specified")

        payload = {"webhook_url": webhook_url, "event": {"types": event_types}}

        response = self._client._request("POST", url, json=payload)
        return response.json()

    def update(
        self, webhook_id: str, webhook_url: str, event_types: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """Point an active webhook at a new URL.

        The event types stay as registered: to change them, delete the webhook
        and add a new one. Before 1.3.1 this method registered a second webhook
        instead, so check ``get()`` for registrations left behind.

        Args:
            webhook_id: The ID of the webhook to update
            webhook_url: The new URL to send webhook notifications to
            event_types: Ignored. Kept so existing calls still work; the API
                never changed event types in place.

        Returns:
            Dictionary containing the update webhook response
        """
        url = f"{self.base_url}/update"

        # The server routes /get, /add, /update and /inactive to one resource
        # and picks the handler by method: PUT updates, POST would add.
        payload = {"webhook_id": webhook_id, "webhook_url": webhook_url}

        response = self._client._request("PUT", url, json=payload)
        return response.json()

    def delete(self, webhook_id: str) -> dict[str, Any]:
        """Delete a webhook by making it inactive.

        Args:
            webhook_id: The ID of the webhook to delete

        Returns:
            Dictionary containing the delete webhook response
        """
        url = f"{self.base_url}/inactive"

        # DELETE deactivates; a GET on this path only lists webhooks.
        params = {"webhook_id": webhook_id}
        response = self._client._request("DELETE", url, params=params)
        return response.json()

    def logs(self, webhook_id: str) -> dict[str, Any]:
        """Get dispatch logs for a webhook.

        Args:
            webhook_id: The ID of the webhook to get logs for

        Returns:
            Dictionary containing the webhook dispatch logs
        """
        url = f"{self.base_url}/dispatch-logs"

        params = {"webhook_id": webhook_id}
        response = self._client._request("GET", url, params=params)
        return response.json()
