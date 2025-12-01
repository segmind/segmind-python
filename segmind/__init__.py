"""Segmind Python SDK.

A Python client for interacting with Segmind APIs including model inference,
PixelFlows, webhooks, file uploads, and more.

Usage:
    import segmind

    # Run a model
    response = segmind.run("seedream-v3-text-to-image", prompt="A sunset")
    with open("image.jpg", "wb") as f:
        f.write(response.content)

    # Upload files
    result = segmind.files.upload("image.png")
    print(result["file_urls"])

    # Run PixelFlows
    result = segmind.pixelflows.run(workflow_id="...", data={...})
"""

from typing import Optional

from segmind.client import SegmindClient

__version__ = "0.1.0"

# Default client (lazily initialized)
_default_client: Optional[SegmindClient] = None


def _get_client() -> SegmindClient:
    """Get or create the default client."""
    global _default_client
    if _default_client is None:
        _default_client = SegmindClient()
    return _default_client


def run(slug: str, **params):
    """Run a model inference request.

    Args:
        slug: Model slug/identifier
        **params: Parameters to pass to the model

    Returns:
        HTTP response from the API

    Example:
        import segmind
        response = segmind.run("seedream-v3-text-to-image", prompt="A sunset")
        with open("image.jpg", "wb") as f:
            f.write(response.content)
    """
    return _get_client().run(slug, **params)


# Namespace proxies
class _Files:
    def upload(self, file_paths):
        """Upload files to Segmind Storage."""
        return _get_client().files.upload(file_paths)


class _PixelFlows:
    def run(self, **kwargs):
        """Run a PixelFlow workflow."""
        return _get_client().pixelflows.run(**kwargs)

    def get_status(self, **kwargs):
        """Get workflow status."""
        return _get_client().pixelflows.get_status(**kwargs)

    def poll(self, **kwargs):
        """Poll for workflow results."""
        return _get_client().pixelflows.poll(**kwargs)


class _Webhooks:
    def get(self):
        """Get all webhooks."""
        return _get_client().webhooks.get()

    def add(self, webhook_url, event_types):
        """Add a webhook."""
        return _get_client().webhooks.add(webhook_url, event_types)

    def update(self, webhook_id, webhook_url, event_types):
        """Update a webhook."""
        return _get_client().webhooks.update(webhook_id, webhook_url, event_types)

    def delete(self, webhook_id):
        """Delete a webhook."""
        return _get_client().webhooks.delete(webhook_id)

    def logs(self, webhook_id):
        """Get webhook logs."""
        return _get_client().webhooks.logs(webhook_id)


class _Models:
    def list(self):
        """List available models."""
        return _get_client().models.list()


class _Generations:
    def list(self, **kwargs):
        """List generations."""
        return _get_client().generations.list(**kwargs)

    def recent(self, model_name):
        """Get recent generations for a model."""
        return _get_client().generations.recent(model_name)


# Module-level namespaces
files = _Files()
pixelflows = _PixelFlows()
webhooks = _Webhooks()
models = _Models()
generations = _Generations()

__all__ = [
    "SegmindClient",
    "run",
    "files",
    "pixelflows",
    "webhooks",
    "models",
    "generations",
]
