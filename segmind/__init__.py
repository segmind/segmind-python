"""Segmind Python SDK.

A Python client for interacting with Segmind APIs including model inference,
PixelFlows, webhooks, file uploads, and more.

Usage:
    import segmind

    # Run a model (v2 async by default — submit + poll until done)
    result = segmind.run("seedance-1-pro", prompt="A sunset")

    # Run a model synchronously (single blocking v1 call)
    response = segmind.run_sync("seedream-v3-text-to-image", prompt="A sunset")
    with open("image.jpg", "wb") as f:
        f.write(response.content)

    # Or split the submit / wait for finer control (custom deadline/cadence)
    job = segmind.submit_async("seedance-1-pro", prompt="A sunset")
    print(job.request_id)
    result = job.wait(timeout=300)

    # Chat with an LLM (async by default) — normalized .text across providers
    reply = segmind.chat("gpt-5.5", prompt="Write a haiku about the sea")
    print(reply.text)

    # Upload files
    result = segmind.files.upload("image.png")
    print(result["file_urls"])

    # Run PixelFlows
    result = segmind.pixelflows.run(workflow_id="...", data={...})

Note (1.1.0, BREAKING): `run` is now async (v2); the old synchronous `run`
is `run_sync`; `run_async` has been removed (use `run`).
"""

from typing import Optional

from segmind.chat import AsyncChatJob, ChatResponse, image_url
from segmind.client import SegmindClient
from segmind.exceptions import SegmindError
from segmind.v2 import (
    DEFAULT_POLL_INTERVAL_S,
    DEFAULT_POLL_TIMEOUT_S,
    AsyncJob,
    InferenceFailed,
    InferenceTimeout,
)

__version__ = "1.1.0"

# Default client (lazily initialized)
_default_client: Optional[SegmindClient] = None


def _get_client() -> SegmindClient:
    """Get or create the default client."""
    global _default_client
    if _default_client is None:
        _default_client = SegmindClient()
    return _default_client


def run(slug: str, **params) -> dict:
    """Run a model inference request — **async (v2) by default** (since 1.1.0).

    Submits to `/v2`, polls until COMPLETED, and returns the final response
    body. For a single blocking v1 call use `run_sync`. For long/video models
    that can exceed the default 600s deadline, use `submit_async` +
    `job.wait(timeout=...)`.

    Args:
        slug: Model slug/identifier
        **params: Parameters to pass to the model (forwarded verbatim, incl.
            any field named `timeout`/`interval` — SEG-339).

    Returns:
        The final response body once the task reaches COMPLETED.

    Example:
        import segmind
        result = segmind.run("seedance-1-pro", prompt="A sunset")
    """
    return _get_client().run(slug, **params)


def run_sync(slug: str, **params):
    """Run a synchronous (v1) model inference request — single blocking call.

    This is the pre-1.1.0 `run` behaviour: returns the raw `httpx.Response`.

    Args:
        slug: Model slug/identifier
        **params: Parameters to pass to the model

    Returns:
        HTTP response from the API

    Example:
        import segmind
        response = segmind.run_sync("seedream-v3-text-to-image", prompt="A sunset")
        with open("image.jpg", "wb") as f:
            f.write(response.content)
    """
    return _get_client().run_sync(slug, **params)


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


def chat(slug: str, **kwargs) -> ChatResponse:
    """LLM chat — **async (v2) by default**, returns a normalized `ChatResponse`.

    Pass either ``messages=[...]`` or ``prompt=...`` plus any model opts. The
    returned `ChatResponse.text` is provider-normalized (OpenAI / Anthropic /
    Gemini). For a single blocking v1 call use `chat_sync`; for a handle use
    `submit_chat`.

    Example:
        import segmind
        reply = segmind.chat("gpt-5.5", prompt="Write a haiku about the sea")
        print(reply.text)
    """
    return _get_client().chat(slug, **kwargs)


def chat_sync(slug: str, **kwargs) -> ChatResponse:
    """LLM chat — synchronous single `POST /v1/{slug}` → `ChatResponse`."""
    return _get_client().chat_sync(slug, **kwargs)


def submit_chat(slug: str, **kwargs) -> AsyncChatJob:
    """Submit an async (v2) chat request; return an `AsyncChatJob` handle.

    The handle exposes `.wait()` / `.status()` / `.result()` returning a
    normalized `ChatResponse`, plus `.request_id`.
    """
    return _get_client().submit_chat(slug, **kwargs)


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
    "AsyncChatJob",
    "AsyncJob",
    "ChatResponse",
    "InferenceFailed",
    "InferenceTimeout",
    "SegmindClient",
    "SegmindError",
    "chat",
    "chat_sync",
    "files",
    "generations",
    "image_url",
    "models",
    "pixelflows",
    "run",
    "run_sync",
    "submit_async",
    "submit_chat",
    "webhooks",
]
