import os
from typing import Optional

import httpx

from segmind.exceptions import raise_for_status


class SegmindClient:
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
        headers = {
            # "Content-Type": "application/json",
            "User-Agent": "segmind-python/0.1.0",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return httpx.Client(
            headers=headers,
            timeout=httpx.Timeout(self.timeout, connect=5.0),
            base_url=self.base_url,
        )

    def run(self, slug: str, **params) -> httpx.Response:
        response = self._client.post(f"/{slug}", json=params)
        raise_for_status(response)
        return response

    def stream(self, slug: str, **params) -> httpx.Response:
        pass
