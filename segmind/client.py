import os
from typing import Optional

import httpx

from segmind import chat as _chat
from segmind import v2 as _v2
from segmind.accounts import Accounts
from segmind.exceptions import raise_for_status
from segmind.files import Files
from segmind.finetune import Finetune
from segmind.generations import Generations
from segmind.models import Models
from segmind.pixelflows import PixelFlows
from segmind.webhooks import Webhooks


class SegmindClient:
    """Main client for interacting with Segmind APIs.

    This client provides access to various Segmind services including
    model inference, PixelFlows, webhooks, file uploads, and more.

    Attributes:
        api_key: API key for authentication
        base_url: Base URL for API requests
        timeout: Timeout for HTTP requests
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.segmind.com/v1",
        timeout: float = 30.0,
    ):
        self.api_key = api_key or os.getenv("SEGMIND_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = self._build_client()

    def _build_client(self) -> httpx.Client:
        """Build and configure the HTTP client.

        Returns:
            Configured httpx.Client instance
        """
        # Local import avoids a load-time circular import (segmind/__init__.py
        # imports this module before it defines __version__); _build_client only
        # runs at instantiation, by which point __version__ is available.
        from segmind import __version__

        headers = {
            # "Content-Type": "application/json",
            # SEG-338: single source of truth — UA version tracks __version__.
            "User-Agent": f"segmind-python-sdk/{__version__}",
            # SEG-319: identifies SDK traffic in spotdb. Heimdall passes
            # X-Initiator through verbatim on sync (-> "SDK-PY") and suffixes
            # "-V2" on the v2-async path (-> "SDK-PY-V2"). Must match the
            # InitiatorType enum in spot-backend or it's coerced to OTHERS.
            # Version detail stays in User-Agent above.
            "X-Initiator": "SDK-PY",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return httpx.Client(
            headers=headers,
            timeout=httpx.Timeout(self.timeout, connect=5.0),
            base_url=self.base_url,
        )

    def run(self, slug: str, **params) -> dict:
        """Run a model inference request — **async (v2) by default**.

        Since 1.1.0 `run` is the v2 queue-backed path: it submits to `/v2`,
        polls until the task is COMPLETED, and returns the final response body
        (the same dict you'd get from `submit_async(...).wait()`). For a single
        blocking v1 call use `run_sync`.

        All ``params`` are forwarded to the model — including any field named
        ``timeout`` or ``interval`` (SEG-339). For a custom deadline/cadence,
        use ``submit_async`` + ``job.wait(timeout=..., interval=...)``; this is
        also the documented path for long/video models that can exceed the
        default 600s deadline.

        Args:
            slug: Model slug/identifier.
            **params: Parameters to pass to the model.

        Returns:
            The final response body once the task reaches COMPLETED.

        Raises:
            v2.InferenceFailed: server returned FAILED.
            v2.InferenceTimeout: the default 600s timeout elapsed before a
                terminal state — for slower models use ``submit_async``.
        """
        return _v2.run(self, slug, **params)

    def run_sync(self, slug: str, **params) -> httpx.Response:
        """Run a synchronous (v1) model inference request — single blocking call.

        This is the pre-1.1.0 `run` behaviour: one `POST /v1/{slug}` that
        blocks until the model responds, returning the raw `httpx.Response`
        (use `.content` for bytes, `.json()` for JSON models).

        Args:
            slug: Model slug/identifier
            **params: Parameters to pass to the model

        Returns:
            HTTP response from the API

        Raises:
            SegmindError: If the request fails
        """
        response = self._client.post(f"/{slug}", json=params)
        raise_for_status(response)
        return response

    def submit_async(self, slug: str, **params) -> "_v2.AsyncJob":
        """Submit a v2 async inference request and return a job handle.

        The handle exposes `wait()`, `status()`, and `result()`. Use `wait()`
        to block until COMPLETED or FAILED. Default poll interval 1.0s,
        timeout 600s — override per-call for very slow models.

        Args:
            slug: Model slug/identifier.
            **params: Parameters to pass to the model.

        Returns:
            AsyncJob handle wrapping the submit response.
        """
        return _v2.submit(self, slug, **params)

    def chat(self, slug: str, **kwargs) -> "_chat.ChatResponse":
        """LLM chat — **async (v2) by default**, mirrors `run`.

        Submits to `/v2`, waits, and returns a provider-normalized
        `ChatResponse` (`.text` works across OpenAI / Anthropic / Gemini
        shapes). Pass either ``messages=[...]`` or ``prompt=...`` plus any
        model opts (`temperature`, `instruction`, `image`, …). For a single
        blocking v1 call use `chat_sync`; for a handle use `submit_chat`.
        """
        return _chat.chat(self, slug, **kwargs)

    def chat_sync(self, slug: str, **kwargs) -> "_chat.ChatResponse":
        """LLM chat — synchronous single `POST /v1/{slug}` → `ChatResponse`."""
        return _chat.chat_sync(self, slug, **kwargs)

    def submit_chat(self, slug: str, **kwargs) -> "_chat.AsyncChatJob":
        """Submit an async (v2) chat request; return an `AsyncChatJob` handle.

        The handle exposes `.wait()` / `.status()` / `.result()` returning a
        normalized `ChatResponse`, plus `.request_id`.
        """
        return _chat.submit_chat(self, slug, **kwargs)

    def stream(self, slug: str, **params):
        """Token streaming (not yet supported by the Segmind gateway).

        Raises:
            NotImplementedError: always — the gateway has no SSE path yet.
        """
        raise NotImplementedError(
            "token streaming is not yet supported by the Segmind gateway"
        )

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        """Make an HTTP request.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: API path (will be appended to base_url)
            **kwargs: Additional arguments to pass to the request

        Returns:
            HTTP response from the API

        Raises:
            HTTPError: If the request fails
        """
        response = self._client.request(method, path, **kwargs)
        raise_for_status(response)
        return response

    @property
    def pixelflows(self) -> PixelFlows:
        """
        Namespace for operations related to PixelFlows.
        """
        return PixelFlows(client=self)

    @property
    def webhooks(self) -> Webhooks:
        """
        Namespace for operations related to Webhooks.
        """
        return Webhooks(client=self)

    @property
    def models(self) -> Models:
        """
        Namespace for operations related to Models.
        """
        return Models(client=self)

    @property
    def files(self) -> Files:
        """
        Namespace for operations related to Files.
        """
        return Files(client=self)

    @property
    def generations(self) -> Generations:
        """
        Namespace for operations related to Generations.
        """
        return Generations(client=self)

    @property
    def accounts(self) -> Accounts:
        """
        Namespace for operations related to Accounts.
        """
        return Accounts(client=self)

    @property
    def finetune(self) -> Finetune:
        """
        Namespace for operations related to Finetuning APIs.
        """
        return Finetune(client=self)
