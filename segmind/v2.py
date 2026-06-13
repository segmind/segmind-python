# ruff: noqa: N818  exception names are deliberately non-Error-suffixed for natural reading in user code
"""v2 async inference for the Segmind Python SDK.

The v2 path is a two-step submit-then-poll: `POST /v2/{slug}` returns a
`request_id` immediately; the actual result lands in Redis once a worker
finishes. Clients poll `/v2/requests/{id}/status` until the task hits
`COMPLETED` or `FAILED`, then GET `/v2/requests/{id}` for the body.

This module provides:

    client.submit_async(slug, **params) -> AsyncJob
    client.run_async(slug, **params)    -> dict      # submit + wait
    AsyncJob.wait(timeout, interval)    -> dict      # block to completion

Defaults are 1.0s poll interval, 600s overall timeout. For slugs known to
be slow (long video, long-running LLM), pass a larger `timeout` and
`interval` per call. For fire-and-forget patterns, use webhooks.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from segmind.exceptions import SegmindError

if TYPE_CHECKING:
    from segmind.client import SegmindClient


DEFAULT_POLL_INTERVAL_S = 1.0
DEFAULT_POLL_TIMEOUT_S = 600.0


class InferenceFailed(SegmindError):
    """Raised when a v2 async request reaches the FAILED state.

    Server-provided error string is in `detail`. The status-endpoint body
    is on `.status_body` for callers that want the raw payload; if you
    need server-side metrics or a fuller failure record, call
    `AsyncJob.result()` separately after catching.
    """

    status_body: dict[str, Any]

    def __init__(self, detail: str | None, status_body: dict[str, Any]) -> None:
        super().__init__(status=None, detail=detail)
        self.status_body = status_body


class InferenceTimeout(SegmindError):
    """Raised when an `AsyncJob.wait()` exceeds its `timeout` before the
    task reaches a terminal state. The job may still be running on the
    server — re-fetch the status URL to confirm and recover the result.
    """

    request_id: str
    elapsed_s: float

    def __init__(self, request_id: str, elapsed_s: float) -> None:
        super().__init__(
            status=None,
            detail=f"v2 request {request_id!r} did not complete within {elapsed_s:.1f}s",
        )
        self.request_id = request_id
        self.elapsed_s = elapsed_s


@dataclass
class AsyncJob:
    """Handle for a v2 async request that has been submitted but not yet completed.

    Returned by `SegmindClient.submit_async()`. Use `wait()` to block until
    a terminal state, or poll `status()` manually if you need finer control.
    """

    request_id: str
    status_url: str
    response_url: str
    submit_response: dict[str, Any]
    _client: SegmindClient = field(repr=False)

    def status(self) -> dict[str, Any]:
        """Fetch the current status payload without blocking.

        Returns the server's body for `GET /v2/requests/{id}/status`. The
        `status` field is one of `QUEUED`, `PROCESSING`, `COMPLETED`,
        `FAILED`. On `FAILED`, the body also includes `error`.
        """
        resp = self._client._request("GET", self.status_url)
        return resp.json()

    def result(self) -> dict[str, Any]:
        """Fetch the final response body. Only meaningful once status is COMPLETED."""
        resp = self._client._request("GET", self.response_url)
        return resp.json()

    def wait(
        self,
        timeout: float = DEFAULT_POLL_TIMEOUT_S,
        interval: float = DEFAULT_POLL_INTERVAL_S,
    ) -> dict[str, Any]:
        """Block until the task reaches a terminal state and return the result.

        Args:
            timeout: Hard deadline in seconds. Raises `InferenceTimeout` if
                exceeded. Default 600s.
            interval: Sleep between status polls. Default 1.0s.

        Returns:
            The server body from `GET /v2/requests/{id}` on COMPLETED.

        Raises:
            InferenceFailed: status reached FAILED. The server error string
                is in `e.detail`; the raw status body in `e.status_body`.
            InferenceTimeout: `timeout` elapsed before a terminal state.
        """
        deadline = time.monotonic() + timeout
        while True:
            status_body = self.status()
            state = status_body.get("status")

            if state == "COMPLETED":
                return self.result()

            if state == "FAILED":
                # /status already carries the error string for FAILED (heimdall
                # SEG-97). Build the exception from the status body directly so
                # we don't pay a second HTTP round-trip on every failure path.
                raise InferenceFailed(
                    detail=status_body.get("error"),
                    status_body=status_body,
                )

            if time.monotonic() >= deadline:
                raise InferenceTimeout(
                    request_id=self.request_id,
                    elapsed_s=timeout,
                )

            time.sleep(interval)


def submit(client: SegmindClient, slug: str, **params) -> AsyncJob:
    """`POST /v2/{slug}`; return an AsyncJob handle for polling."""
    url = _v2_base(client) + "/" + slug.lstrip("/")
    resp = client._request("POST", url, json=params)
    body = resp.json()

    request_id = body.get("request_id")
    status_url = body.get("status_url")
    response_url = body.get("response_url")
    if not (request_id and status_url and response_url):
        # Server's contract is to always return these three on a successful
        # submit. If we got a 2xx without them, something is genuinely off
        # — fail loudly rather than poll forever on an unknown URL.
        raise SegmindError(
            status=resp.status_code,
            detail=(
                "v2 submit returned 2xx but is missing request_id / status_url / "
                f"response_url; got keys={sorted(body.keys())}"
            ),
        )

    return AsyncJob(
        request_id=request_id,
        status_url=status_url,
        response_url=response_url,
        submit_response=body,
        _client=client,
    )


def run(
    client: SegmindClient,
    slug: str,
    *,
    timeout: float = DEFAULT_POLL_TIMEOUT_S,
    interval: float = DEFAULT_POLL_INTERVAL_S,
    **params,
) -> dict[str, Any]:
    """One-shot convenience: submit and wait. Equivalent to
    `client.submit_async(slug, **params).wait(timeout, interval)`.
    """
    job = submit(client, slug, **params)
    return job.wait(timeout=timeout, interval=interval)


def _v2_base(client: SegmindClient) -> str:
    """Derive the v2 prefix from the client's `base_url`.

    The default client base_url is `https://api.segmind.com/v1`; the v2
    endpoint sits at `https://api.segmind.com/v2`. We strip the trailing
    `/vN` segment and append `/v2` so callers who override base_url for
    staging (`api-latest.segmind.com/v1`) keep working without extra
    config.
    """
    base = client.base_url.rstrip("/")
    if "/" in base and base.rsplit("/", 1)[1].startswith("v"):
        base = base.rsplit("/", 1)[0]
    return base + "/v2"
