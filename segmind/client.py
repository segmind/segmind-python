import os
from typing import Optional

import httpx

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
        headers = {
            # "Content-Type": "application/json",
            "User-Agent": "segmind-python-sdk/0.1.0",
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

    def run(self, slug: str, **params) -> httpx.Response:
        """Run a model inference request.

        Args:
            slug: Model slug/identifier
            **params: Parameters to pass to the model

        Returns:
            HTTP response from the API

        Raises:
            HTTPError: If the request fails
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

    def run_async(
        self,
        slug: str,
        *,
        timeout: float = _v2.DEFAULT_POLL_TIMEOUT_S,
        interval: float = _v2.DEFAULT_POLL_INTERVAL_S,
        **params,
    ) -> dict:
        """One-shot v2 async inference: submit + wait. Returns the final
        response body (the same dict you'd get from polling to COMPLETED).

        Args:
            slug: Model slug/identifier.
            timeout: Hard deadline in seconds (default 600s).
            interval: Status-poll cadence (default 1.0s).
            **params: Parameters to pass to the model.

        Raises:
            v2.InferenceFailed: server returned FAILED.
            v2.InferenceTimeout: timeout elapsed before terminal state.
        """
        return _v2.run(self, slug, timeout=timeout, interval=interval, **params)

    def stream(self, slug: str, **params) -> httpx.Response:
        """Stream a model inference request (not implemented).

        Args:
            slug: Model slug/identifier
            **params: Parameters to pass to the model

        Returns:
            HTTP response from the API
        """
        pass

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
