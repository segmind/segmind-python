from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from segmind.client import SegmindClient


class Webhooks:
    """Client for Segmind Webhooks API."""

    def __init__(self, client: "SegmindClient"):
        """Initialize Webhooks client.

        Args:
            client: SegmindClient instance to use for API calls.
        """
        self.client = client
        self.base_url = "https://api.spotprod.segmind.com/webhook"

    def get(self) -> dict[str, Any]:
        """Get all webhooks.

        Returns:
            Dictionary containing the webhooks response
        """
        self.get_url = f"{self.base_url}/get"

        response = self.client._client.get(self.get_url)
        response.raise_for_status()
        return response.json()

    def add(self, webhook_url: str, event_types: list[str]) -> dict[str, Any]:
        """Add a new webhook.

        Args:
            webhook_url: The URL to send webhook notifications to
            event_types: List of event types to subscribe to (default: ["PIXELFLOW"])

        Returns:
            Dictionary containing the add webhook response
        """
        self.add_url = f"{self.base_url}/add"

        if not event_types:
            raise ValueError("Event types must be specified")

        payload = {"webhook_url": webhook_url, "event": {"types": event_types}}

        response = self.client._client.post(self.add_url, json=payload)
        response.raise_for_status()
        return response.json()

    def update(self, webhook_id: str, webhook_url: str, event_types: list[str]) -> dict[str, Any]:
        """Update an existing webhook.

        Args:
            webhook_id: The ID of the webhook to update
            webhook_url: The new URL to send webhook notifications to
            event_types: List of event types to subscribe to (default: ["PIXELFLOW"])

        Returns:
            Dictionary containing the update webhook response
        """
        self.update_url = f"{self.base_url}/update"

        if not event_types:
            raise ValueError("Event types must be specified")

        payload = {
            "webhook_id": webhook_id,
            "webhook_url": webhook_url,
            "event": {"types": event_types},
        }

        response = self.client._client.post(self.update_url, json=payload)
        response.raise_for_status()
        return response.json()

    def delete(self, webhook_id: str) -> dict[str, Any]:
        """Delete a webhook by making it inactive.

        Args:
            webhook_id: The ID of the webhook to delete

        Returns:
            Dictionary containing the delete webhook response
        """
        self.delete_url = f"{self.base_url}/inactive"

        params = {"webhook_id": webhook_id}
        response = self.client._client.get(self.delete_url, params=params)
        response.raise_for_status()
        return response.json()

    def logs(self, webhook_id: str) -> dict[str, Any]:
        """Get dispatch logs for a webhook.

        Args:
            webhook_id: The ID of the webhook to get logs for

        Returns:
            Dictionary containing the webhook dispatch logs
        """
        self.logs_url = f"{self.base_url}/dispatch-logs"

        params = {"webhook_id": webhook_id}
        response = self.client._client.get(self.logs_url, params=params)
        response.raise_for_status()
        return response.json()
