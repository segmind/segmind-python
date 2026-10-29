import warnings
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
        """Change the URL an existing webhook delivers to.

        The webhook keeps its id, signing secret and event types. The server
        cannot change event types in place: to subscribe to different events,
        ``delete()`` the webhook and ``add()`` a new one. Before 1.3.1 this
        method registered a second webhook instead, so check ``get()`` for
        registrations left behind.

        Args:
            webhook_id: The ID of the webhook to update
            webhook_url: The new URL to send webhook notifications to
            event_types: Ignored, kept so existing calls still work. Passing it
                emits a ``UserWarning``.

        Returns:
            Dictionary containing the update webhook response
        """
        if event_types is not None:
            warnings.warn(
                "webhooks.update() changes the URL only; event_types is ignored. "
                "To change event types, delete() the webhook and add() a new one.",
                UserWarning,
                stacklevel=2,
            )

        url = f"{self.base_url}/update"
        payload = {"webhook_id": webhook_id, "webhook_url": webhook_url}

        # One server resource serves /get, /add, /update and /inactive and
        # dispatches on the HTTP method, so update must be a PUT: a POST here
        # registers a second webhook instead.
        response = self._client._request("PUT", url, json=payload)
        return response.json()

    def delete(self, webhook_id: str) -> dict[str, Any]:
        """Deactivate a webhook so it stops receiving events.

        Args:
            webhook_id: The ID of the webhook to delete

        Returns:
            Dictionary containing the delete webhook response
        """
        url = f"{self.base_url}/inactive"

        # A GET here would only list your webhooks; DELETE deactivates.
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
