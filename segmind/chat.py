"""LLM chat surface + output normalization for the Segmind Python SDK (SEG-344).

The Segmind gateway is a transparent passthrough: it returns each LLM
provider's **raw native JSON** unchanged, in three incompatible shapes —

    OpenAI    : choices[0].message.content
    Anthropic : content[0].text          (content is a list of {type,text} parts)
    Gemini    : candidates[0].content.parts[0].text

This module hides that asymmetry behind `ChatResponse`, whose `.text`
returns the assistant string regardless of provider. The raw provider body
is always preserved on `.raw`.

Verb surface (mirrors `run` per SEG-354 — async is the default):

    client.chat(slug, messages=/prompt=, **opts)   -> ChatResponse   # ASYNC (v2)
    client.chat_sync(slug, messages=/prompt=, **opts) -> ChatResponse # SYNC  (v1)
    client.submit_chat(slug, ...)                  -> AsyncChatJob    # async handle

`chat()` is `submit_chat().wait()` with the default poll cadence (inherits
the v2 600s deadline). For a custom deadline/cadence use
`submit_chat(...).wait(timeout=..., interval=...)`.

Out of scope for v1 (see SEG-344): `.tool_calls` is parsed best-effort but
stays empty until the gateway forwards `tools` (B1); `stream()` raises
`NotImplementedError` until the gateway grows SSE (B3).
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from segmind import v2 as _v2
from segmind.exceptions import SegmindError, raise_for_status

if TYPE_CHECKING:
    from segmind.client import SegmindClient


# ---------------------------------------------------------------------------
# Output normalization
# ---------------------------------------------------------------------------


def _extract_text(raw: dict[str, Any]) -> str | None:
    """Pull the assistant text out of any of the 3 provider shapes.

    Structural provider-sniff (not a `model` string match — the gateway does
    not echo a stable provider tag): the presence of a distinctive top-level
    key decides the shape. Returns None if no text could be located (caller's
    `.text` raises a helpful error in that case).
    """
    if not isinstance(raw, dict):
        return None

    # OpenAI: {"choices": [{"message": {"content": "..."}}]}
    if "choices" in raw:
        choices = raw.get("choices") or []
        if choices:
            msg = (choices[0] or {}).get("message") or {}
            content = msg.get("content")
            if isinstance(content, str):
                return content
            # Some OpenAI-compat backends return content as a list of parts.
            if isinstance(content, list):
                return "".join(
                    part.get("text", "")
                    for part in content
                    if isinstance(part, dict) and part.get("type") in (None, "text")
                )
        return None

    # Anthropic: {"content": [{"type": "text", "text": "..."}]}
    if isinstance(raw.get("content"), list):
        return "".join(
            part.get("text", "")
            for part in raw["content"]
            if isinstance(part, dict) and part.get("type") == "text"
        )

    # Gemini: {"candidates": [{"content": {"parts": [{"text": "..."}]}}]}
    if "candidates" in raw:
        candidates = raw.get("candidates") or []
        if candidates:
            parts = ((candidates[0] or {}).get("content") or {}).get("parts") or []
            return "".join(p.get("text", "") for p in parts if isinstance(p, dict))
        return None

    return None


def _extract_usage(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Return the provider's token-usage block (shape varies by provider)."""
    if not isinstance(raw, dict):
        return None
    # OpenAI + Anthropic both use "usage"; Gemini uses "usageMetadata".
    return raw.get("usage") or raw.get("usageMetadata")


def _extract_finish_reason(raw: dict[str, Any]) -> str | None:
    if not isinstance(raw, dict):
        return None
    if "choices" in raw:
        choices = raw.get("choices") or []
        return (choices[0] or {}).get("finish_reason") if choices else None
    if "stop_reason" in raw:  # Anthropic
        return raw.get("stop_reason")
    if "candidates" in raw:  # Gemini
        candidates = raw.get("candidates") or []
        return (candidates[0] or {}).get("finishReason") if candidates else None
    return None


def _extract_tool_calls(raw: dict[str, Any]) -> list[Any]:
    """Best-effort tool-call extraction.

    Stays empty in practice until Heimdall forwards `tools` to the provider
    (SEG-344 B1); surfaced structurally so it lights up for free once the
    gateway does. OpenAI puts them on `choices[0].message.tool_calls`.
    """
    if not isinstance(raw, dict):
        return []
    if "choices" in raw:
        choices = raw.get("choices") or []
        if choices:
            return (choices[0] or {}).get("message", {}).get("tool_calls") or []
    return []


@dataclass
class ChatResponse:
    """Normalized view over an LLM provider's raw chat response.

    `.raw` is always the provider's native JSON (OpenAI / Anthropic / Gemini
    shape). Everything else is derived from it, so you can drop down to `.raw`
    whenever the normalization doesn't cover a provider-specific field.
    """

    raw: dict[str, Any]

    @property
    def text(self) -> str:
        """The assistant's text reply, normalized across providers.

        Raises:
            SegmindError: if no assistant text could be located in `.raw`
                (e.g. a content-filtered empty body, or a non-LLM response).
                Inspect `.raw` to see what the provider actually returned.
        """
        text = _extract_text(self.raw)
        if text is None:
            keys = sorted(self.raw.keys()) if isinstance(self.raw, dict) else type(self.raw)
            raise SegmindError(
                status=None,
                detail=(
                    "could not extract assistant text from the response "
                    f"(top-level keys={keys}); inspect ChatResponse.raw"
                ),
            )
        return text

    def json(self) -> Any:
        """Parse `.text` as JSON (for JSON-mode / structured outputs).

        Raises:
            SegmindError: if `.text` is not valid JSON.
        """
        try:
            return json.loads(self.text)
        except (ValueError, TypeError) as exc:
            raise SegmindError(
                status=None,
                detail=f"ChatResponse.text is not valid JSON: {exc}",
            ) from exc

    @property
    def usage(self) -> dict[str, Any] | None:
        """Provider token-usage block (`usage` / `usageMetadata`), or None."""
        return _extract_usage(self.raw)

    @property
    def finish_reason(self) -> str | None:
        """Provider stop reason (`finish_reason` / `stop_reason` / `finishReason`)."""
        return _extract_finish_reason(self.raw)

    @property
    def tool_calls(self) -> list[Any]:
        """Tool calls, if any. Empty until the gateway forwards `tools` (B1)."""
        return _extract_tool_calls(self.raw)


# ---------------------------------------------------------------------------
# Multimodal input helper
# ---------------------------------------------------------------------------


def image_url(url_or_path: str) -> dict[str, Any]:
    """Build an OpenAI-style image content-part for use inside `messages`.

    A local file path is read and base64-encoded into a `data:` URI; an
    `http(s)://` (or already-`data:`) URL is passed through. The data-URI
    route is recommended — the gateway's URL-fetch path 400s on some hosts
    (SEG-344 B5), so local files are safest inlined.

    Example:
        msg = {"role": "user", "content": [
            {"type": "text", "text": "What's in this image?"},
            image_url("cat.png"),
        ]}
    """
    lowered = url_or_path.lower()
    if lowered.startswith(("http://", "https://", "data:")):
        uri = url_or_path
    elif os.path.isfile(url_or_path):
        mime, _ = mimetypes.guess_type(url_or_path)
        mime = mime or "application/octet-stream"
        with open(url_or_path, "rb") as fh:
            b64 = base64.b64encode(fh.read()).decode("ascii")
        uri = f"data:{mime};base64,{b64}"
    else:
        raise SegmindError(
            status=None,
            detail=(
                f"image_url: {url_or_path!r} is neither an existing file nor an "
                "http(s)/data URL"
            ),
        )
    return {"type": "image_url", "image_url": {"url": uri}}


# ---------------------------------------------------------------------------
# Request-body construction
# ---------------------------------------------------------------------------


def _build_body(
    messages: list[dict[str, Any]] | None,
    prompt: str | None,
    opts: dict[str, Any],
) -> dict[str, Any]:
    """Assemble the chat request body.

    Accepts EITHER `messages` (OpenAI-style list) or `prompt` (the flat
    convenience field the gateway also honours). Extra kwargs are forwarded
    verbatim so model params like `temperature` / `instruction` / `image`
    pass straight through. At least one of messages/prompt is required.
    """
    if messages is None and prompt is None:
        raise SegmindError(
            status=None,
            detail="chat: pass either messages=[...] or prompt=...",
        )
    body: dict[str, Any] = dict(opts)
    if messages is not None:
        body["messages"] = messages
    if prompt is not None:
        body["prompt"] = prompt
    return body


def _raw_from_v2_body(body: dict[str, Any]) -> dict[str, Any]:
    """Pull the provider JSON out of a v2 async result body.

    The v2 `output` field is a **stringified** copy of the provider's native
    JSON (double-encoded), so decode it before normalizing. Tolerate the case
    where a future gateway returns it already-parsed (dict), or where there's
    no `output` key at all (fall back to the whole body).
    """
    output = body.get("output")
    if isinstance(output, str):
        try:
            return json.loads(output)
        except ValueError:
            # Not JSON — treat the string as the text payload directly so
            # `.text` still works rather than raising on a plain-text reply.
            return {"choices": [{"message": {"content": output}}]}
    if isinstance(output, dict):
        return output
    return body


# ---------------------------------------------------------------------------
# Async chat handle
# ---------------------------------------------------------------------------


@dataclass
class AsyncChatJob:
    """Async chat handle — thin `ChatResponse`-returning wrapper over `AsyncJob`.

    Returned by `submit_chat()`. `wait()` / `result()` return a normalized
    `ChatResponse`; `status()` / `request_id` proxy straight through to the
    underlying v2 job for parity with `submit_async`.
    """

    job: _v2.AsyncJob = field(repr=False)

    @property
    def request_id(self) -> str:
        return self.job.request_id

    def status(self) -> dict[str, Any]:
        """Current v2 status payload (QUEUED / PROCESSING / COMPLETED / FAILED)."""
        return self.job.status()

    def result(self) -> ChatResponse:
        """Normalized result. Only meaningful once status is COMPLETED."""
        return ChatResponse(raw=_raw_from_v2_body(self.job.result()))

    def wait(
        self,
        timeout: float = _v2.DEFAULT_POLL_TIMEOUT_S,
        interval: float = _v2.DEFAULT_POLL_INTERVAL_S,
    ) -> ChatResponse:
        """Block until the task completes, then return a `ChatResponse`.

        Raises `InferenceFailed` / `InferenceTimeout` like `AsyncJob.wait`.
        """
        return ChatResponse(raw=_raw_from_v2_body(self.job.wait(timeout, interval)))


# ---------------------------------------------------------------------------
# Verbs
# ---------------------------------------------------------------------------


def submit_chat(
    client: SegmindClient,
    slug: str,
    *,
    messages: list[dict[str, Any]] | None = None,
    prompt: str | None = None,
    stream: bool = False,
    **opts,
) -> AsyncChatJob:
    """Submit an async (v2) chat request; return an `AsyncChatJob` handle."""
    if stream:
        raise NotImplementedError(
            "token streaming is not yet supported by the Segmind gateway"
        )
    body = _build_body(messages, prompt, opts)
    return AsyncChatJob(job=_v2.submit(client, slug, **body))


def chat(
    client: SegmindClient,
    slug: str,
    *,
    messages: list[dict[str, Any]] | None = None,
    prompt: str | None = None,
    stream: bool = False,
    **opts,
) -> ChatResponse:
    """Async chat (default): submit to `/v2`, wait, return a `ChatResponse`.

    Mirrors `run` — async is the default. For a custom deadline/cadence use
    `submit_chat(...).wait(timeout=..., interval=...)`; for a single blocking
    `/v1` call use `chat_sync(...)`.
    """
    return submit_chat(
        client, slug, messages=messages, prompt=prompt, stream=stream, **opts
    ).wait()


def chat_sync(
    client: SegmindClient,
    slug: str,
    *,
    messages: list[dict[str, Any]] | None = None,
    prompt: str | None = None,
    stream: bool = False,
    **opts,
) -> ChatResponse:
    """Sync chat: single blocking `POST /v1/{slug}`, return a `ChatResponse`."""
    if stream:
        raise NotImplementedError(
            "token streaming is not yet supported by the Segmind gateway"
        )
    body = _build_body(messages, prompt, opts)
    resp = client._client.post(f"/{slug}", json=body)
    raise_for_status(resp)
    try:
        raw = resp.json()
    except ValueError as exc:
        raise SegmindError(
            status=resp.status_code,
            detail=f"chat_sync: response body was not JSON: {exc}",
        ) from exc
    return ChatResponse(raw=raw)
