"""Unit tests for the LLM chat surface + ChatResponse normalization (SEG-344).

All HTTP traffic is mocked with respx; no network required.
"""

from __future__ import annotations

import base64
import json

import httpx
import pytest
import respx

import segmind
from segmind import AsyncChatJob, ChatResponse, SegmindClient, image_url

API_HOST = "https://api.segmind.com"
SLUG = "gpt-5.5"
REQ_ID = "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"

# --- the 3 raw provider shapes the gateway passes through verbatim ----------

OPENAI_RAW = {
    "choices": [
        {"message": {"role": "assistant", "content": "Hello from OpenAI"},
         "finish_reason": "stop"}
    ],
    "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
}
ANTHROPIC_RAW = {
    "content": [{"type": "text", "text": "Hello from Anthropic"}],
    "stop_reason": "end_turn",
    "usage": {"input_tokens": 5, "output_tokens": 3},
}
GEMINI_RAW = {
    "candidates": [
        {"content": {"parts": [{"text": "Hello from "}, {"text": "Gemini"}]},
         "finishReason": "STOP"}
    ],
    "usageMetadata": {"promptTokenCount": 5, "candidatesTokenCount": 3},
}


@pytest.fixture
def client():
    return SegmindClient(api_key="sk-test", base_url=f"{API_HOST}/v1")


# ---- A1: output normalization (.text across 3 provider shapes) --------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        (OPENAI_RAW, "Hello from OpenAI"),
        (ANTHROPIC_RAW, "Hello from Anthropic"),
        (GEMINI_RAW, "Hello from Gemini"),
    ],
)
def test_text_normalizes_all_three_provider_shapes(raw, expected):
    assert ChatResponse(raw=raw).text == expected


def test_raw_is_always_preserved():
    cr = ChatResponse(raw=OPENAI_RAW)
    assert cr.raw is OPENAI_RAW


def test_text_raises_helpful_error_when_no_text_found():
    cr = ChatResponse(raw={"unexpected": "shape"})
    with pytest.raises(segmind.SegmindError) as exc:
        _ = cr.text
    assert "could not extract assistant text" in (exc.value.detail or "")


# ---- A3: ChatResponse fields -----------------------------------------------


def test_usage_finish_reason_per_provider():
    o = ChatResponse(raw=OPENAI_RAW)
    assert o.usage == OPENAI_RAW["usage"]
    assert o.finish_reason == "stop"

    a = ChatResponse(raw=ANTHROPIC_RAW)
    assert a.usage == ANTHROPIC_RAW["usage"]
    assert a.finish_reason == "end_turn"

    g = ChatResponse(raw=GEMINI_RAW)
    assert g.usage == GEMINI_RAW["usageMetadata"]
    assert g.finish_reason == "STOP"


def test_tool_calls_empty_by_default_but_structural():
    assert ChatResponse(raw=OPENAI_RAW).tool_calls == []
    raw = {
        "choices": [
            {"message": {"content": None, "tool_calls": [{"id": "call_1"}]}}
        ]
    }
    assert ChatResponse(raw=raw).tool_calls == [{"id": "call_1"}]


def test_json_parses_json_mode_output_or_raises():
    cr = ChatResponse(
        raw={"choices": [{"message": {"content": '{"a": 1, "b": [2, 3]}'}}]}
    )
    assert cr.json() == {"a": 1, "b": [2, 3]}

    with pytest.raises(segmind.SegmindError):
        ChatResponse(raw=OPENAI_RAW).json()  # "Hello from OpenAI" is not JSON


# ---- A5: image_url helper ---------------------------------------------------


def test_image_url_passes_through_http_url():
    part = image_url("https://example.com/cat.png")
    assert part == {
        "type": "image_url",
        "image_url": {"url": "https://example.com/cat.png"},
    }


def test_image_url_base64_encodes_local_file(tmp_path):
    f = tmp_path / "pixel.png"
    payload = b"\x89PNG\r\n\x1a\n_fake_png_bytes"
    f.write_bytes(payload)

    part = image_url(str(f))
    uri = part["image_url"]["url"]
    assert uri.startswith("data:image/png;base64,")
    decoded = base64.b64decode(uri.split(",", 1)[1])
    assert decoded == payload


def test_image_url_rejects_unknown_target():
    with pytest.raises(segmind.SegmindError):
        image_url("/no/such/file.png")


# ---- A2: chat_sync (v1) -----------------------------------------------------


@respx.mock
def test_chat_sync_posts_v1_and_normalizes(client):
    route = respx.post(f"{API_HOST}/v1/{SLUG}").mock(
        return_value=httpx.Response(200, json=OPENAI_RAW)
    )

    reply = client.chat_sync(SLUG, prompt="hi", temperature=0.5)

    assert isinstance(reply, ChatResponse)
    assert reply.text == "Hello from OpenAI"
    sent = json.loads(route.calls.last.request.content)
    assert sent == {"prompt": "hi", "temperature": 0.5}


@respx.mock
def test_chat_sync_accepts_messages(client):
    route = respx.post(f"{API_HOST}/v1/{SLUG}").mock(
        return_value=httpx.Response(200, json=ANTHROPIC_RAW)
    )
    msgs = [{"role": "user", "content": "hi"}]

    reply = client.chat_sync(SLUG, messages=msgs)

    assert reply.text == "Hello from Anthropic"
    sent = json.loads(route.calls.last.request.content)
    assert sent == {"messages": msgs}


def test_chat_requires_messages_or_prompt(client):
    with pytest.raises(segmind.SegmindError):
        client.chat_sync(SLUG)


# ---- A4: async chat (chat / submit_chat) -----------------------------------

# v2 wraps the provider JSON as a *stringified* `output`.
V2_BODY = {
    "status": "COMPLETED",
    "error": None,
    "metrics": {"inference_time": 0.4},
    "output": json.dumps(OPENAI_RAW),
}


def _mock_v2_complete():
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(
        return_value=httpx.Response(
            200,
            json={
                "request_id": REQ_ID,
                "status": "QUEUED",
                "status_url": f"{API_HOST}/v2/requests/{REQ_ID}/status",
                "response_url": f"{API_HOST}/v2/requests/{REQ_ID}",
            },
        )
    )
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}/status").mock(
        return_value=httpx.Response(200, json={"status": "COMPLETED"})
    )
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}").mock(
        return_value=httpx.Response(200, json=V2_BODY)
    )


@respx.mock
def test_chat_async_default_decodes_stringified_output(client):
    """`chat` is async by default (SEG-354): submit to /v2, wait, then
    json.loads the stringified `output` before normalizing."""
    _mock_v2_complete()

    reply = client.chat(SLUG, prompt="hi")

    assert isinstance(reply, ChatResponse)
    assert reply.text == "Hello from OpenAI"
    assert reply.finish_reason == "stop"


@respx.mock
def test_submit_chat_returns_handle(client):
    _mock_v2_complete()

    job = client.submit_chat(SLUG, prompt="hi")
    assert isinstance(job, AsyncChatJob)
    assert job.request_id == REQ_ID
    assert job.status()["status"] == "COMPLETED"

    reply = job.wait(timeout=5, interval=0.01)
    assert reply.text == "Hello from OpenAI"


@respx.mock
def test_chat_async_handles_plain_string_output(client):
    """If a future gateway returns a non-JSON plain-text `output`, `.text`
    still works rather than blowing up."""
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(
        return_value=httpx.Response(
            200,
            json={
                "request_id": REQ_ID,
                "status": "QUEUED",
                "status_url": f"{API_HOST}/v2/requests/{REQ_ID}/status",
                "response_url": f"{API_HOST}/v2/requests/{REQ_ID}",
            },
        )
    )
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}/status").mock(
        return_value=httpx.Response(200, json={"status": "COMPLETED"})
    )
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}").mock(
        return_value=httpx.Response(
            200, json={"status": "COMPLETED", "output": "just text"}
        )
    )

    assert client.chat(SLUG, prompt="hi").text == "just text"


# ---- A6: streaming stub -----------------------------------------------------


def test_chat_stream_kwarg_raises_not_implemented(client):
    with pytest.raises(NotImplementedError):
        client.chat(SLUG, prompt="hi", stream=True)
    with pytest.raises(NotImplementedError):
        client.chat_sync(SLUG, prompt="hi", stream=True)
    with pytest.raises(NotImplementedError):
        client.submit_chat(SLUG, prompt="hi", stream=True)


# ---- module-level surface ---------------------------------------------------


def test_module_exports_chat_surface():
    for name in ("chat", "chat_sync", "submit_chat", "image_url",
                 "ChatResponse", "AsyncChatJob"):
        assert hasattr(segmind, name), name
        assert name in segmind.__all__, name
