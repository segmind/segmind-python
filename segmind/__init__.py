"""Segmind Python SDK.

A Python client for interacting with Segmind APIs including model inference,
PixelFlows, webhooks, file uploads, and more.

Usage:
    import segmind

    # Run a model (sync v1)
    response = segmind.run("seedream-v3-text-to-image", prompt="A sunset")
    with open("image.jpg", "wb") as f:
        f.write(response.content)

    # Run a model (v2 async — submit + poll until done)
    result = segmind.run_async("seedance-1-pro", prompt="A sunset", timeout=300)

    # Or split the submit / wait for finer control
    job = segmind.submit_async("seedance-1-pro", prompt="A sunset")
    print(job.request_id)
    result = job.wait(timeout=300)

    # Upload files
    result = segmind.files.upload("image.png")
    print(result["file_urls"])

    # Run PixelFlows
    result = segmind.pixelflows.run(workflow_id="...", data={...})
"""

from typing import Optional

from segmind.client import SegmindClient
from segmind.v2 import (
    DEFAULT_POLL_INTERVAL_S,
    DEFAULT_POLL_TIMEOUT_S,
    AsyncJob,
    InferenceFailed,
    InferenceTimeout,
)

__version__ = "1.0.1"

# Default client (lazily initialized)
_default_client: Optional[SegmindClient] = None


def _get_client() -> SegmindClient:
    """Get or create the default client."""
    global _default_client
    if _default_client is None:
        _default_client = SegmindClient()
    return _default_client


def run(slug: str, **params):
    """Run a sync (v1) model inference request.

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


def submit_async(slug: str, **params) -> AsyncJob:
    """Submit a v2 async inference request and return a job handle.

    The handle exposes `.wait()`, `.status()`, and `.result()`. Use `.wait()`
    to block until COMPLETED or FAILED. Useful when you want to track the
    request_id, run other work in parallel, or batch many submissions.

    Args:
        slug: Model slug/identifier.
        **params: Parameters to pass to the model.

    Example:
        import segmind
        job = segmind.submit_async("seedance-1-pro", prompt="A sunset")
        print(job.request_id)
        result = job.wait(timeout=300)
    """
    return _get_client().submit_async(slug, **params)


def run_async(
    slug: str,
    *,
    timeout: float = DEFAULT_POLL_TIMEOUT_S,
    interval: float = DEFAULT_POLL_INTERVAL_S,
    **params,
) -> dict:
    """Run a v2 async inference request to completion (submit + poll).

    Args:
        slug: Model slug/identifier.
        timeout: Hard deadline in seconds (default 600s).
        interval: Status-poll cadence (default 1.0s).
        **params: Parameters to pass to the model.

    Returns:
        The final response body once the task reaches COMPLETED.

    Raises:
        segmind.InferenceFailed: server returned FAILED.
        segmind.InferenceTimeout: timeout elapsed before terminal state.

    Example:
        import segmind
        result = segmind.run_async("seedance-1-pro", prompt="A sunset", timeout=300)
    """
    return _get_client().run_async(slug, timeout=timeout, interval=interval, **params)


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
    "DEFAULT_POLL_INTERVAL_S",
    "DEFAULT_POLL_TIMEOUT_S",
    "AsyncJob",
    "InferenceFailed",
    "InferenceTimeout",
    "SegmindClient",
    "files",
    "generations",
    "models",
    "pixelflows",
    "run",
    "run_async",
    "submit_async",
    "webhooks",
]
