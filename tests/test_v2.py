"""Unit tests for the v2 async helpers.

All HTTP traffic is mocked with respx; no network required.
"""

from __future__ import annotations

import os
from unittest.mock import patch

import httpx
import pytest
import respx

import segmind
from segmind import AsyncJob, InferenceFailed, InferenceTimeout, SegmindClient

API_HOST = "https://api.segmind.com"
SLUG = "mock-inference"
REQ_ID = "11111111-2222-3333-4444-555555555555"

SUBMIT_BODY = {
    "request_id": REQ_ID,
    "status": "QUEUED",
    "poll_url": f"{API_HOST}/v1/requests/{REQ_ID}",
    "response_url": f"{API_HOST}/v2/requests/{REQ_ID}",
    "status_url": f"{API_HOST}/v2/requests/{REQ_ID}/status",
}
RESULT_BODY = {
    "status": "COMPLETED",
    "error": None,
    "metrics": {"inference_time": 0.5},
    "output": "ok",
}


@pytest.fixture
def client():
    """A SegmindClient with a fake API key so the test doesn't depend on env."""
    return SegmindClient(api_key="sk-test", base_url=f"{API_HOST}/v1")


# ---- submit ----------------------------------------------------------------


@respx.mock
def test_submit_async_returns_job_with_urls(client):
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(return_value=httpx.Response(200, json=SUBMIT_BODY))

    job = client.submit_async(SLUG, sleep=1, credits=1e-6)

    assert isinstance(job, AsyncJob)
    assert job.request_id == REQ_ID
    assert job.status_url.endswith(f"/v2/requests/{REQ_ID}/status")
    assert job.response_url.endswith(f"/v2/requests/{REQ_ID}")
    assert job.submit_response["status"] == "QUEUED"


@respx.mock
def test_submit_async_propagates_4xx_as_segmind_error(client):
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(
        return_value=httpx.Response(401, json={"error": "Invalid API key"})
    )

    with pytest.raises(segmind.SegmindError if hasattr(segmind, "SegmindError") else Exception):
        client.submit_async(SLUG)


@respx.mock
def test_submit_raises_when_response_is_missing_request_id(client):
    """If the server's 2xx body lacks request_id, we must fail loudly rather
    than swallow it and poll forever on a missing URL."""
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(
        return_value=httpx.Response(200, json={"status": "QUEUED"}),
    )

    from segmind.exceptions import SegmindError

    with pytest.raises(SegmindError) as exc:
        client.submit_async(SLUG)

    assert "missing request_id" in str(exc.value).lower()


# ---- wait ------------------------------------------------------------------


@respx.mock
def test_wait_returns_result_on_completed(client):
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(return_value=httpx.Response(200, json=SUBMIT_BODY))
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}/status").mock(
        return_value=httpx.Response(200, json={"status": "COMPLETED"})
    )
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}").mock(
        return_value=httpx.Response(200, json=RESULT_BODY)
    )

    job = client.submit_async(SLUG)
    out = job.wait(timeout=5, interval=0.01)

    assert out == RESULT_BODY


@respx.mock
def test_wait_polls_until_completed(client):
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(return_value=httpx.Response(200, json=SUBMIT_BODY))
    # First two polls report QUEUED then PROCESSING, third reports COMPLETED.
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}/status").mock(
        side_effect=[
            httpx.Response(200, json={"status": "QUEUED"}),
            httpx.Response(200, json={"status": "PROCESSING"}),
            httpx.Response(200, json={"status": "COMPLETED"}),
        ]
    )
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}").mock(
        return_value=httpx.Response(200, json=RESULT_BODY)
    )

    out = client.submit_async(SLUG).wait(timeout=5, interval=0.01)

    assert out == RESULT_BODY


@respx.mock
def test_wait_raises_inference_failed_on_failed(client):
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(return_value=httpx.Response(200, json=SUBMIT_BODY))
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}/status").mock(
        return_value=httpx.Response(200, json={"status": "FAILED", "error": "boom"})
    )
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}").mock(
        return_value=httpx.Response(
            200,
            json={"status": "FAILED", "error": "boom", "metrics": {}},
        )
    )

    job = client.submit_async(SLUG)
    with pytest.raises(InferenceFailed) as exc:
        job.wait(timeout=5, interval=0.01)

    assert exc.value.detail == "boom"
    assert exc.value.response_body["status"] == "FAILED"


@respx.mock
def test_wait_raises_inference_timeout(client):
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(return_value=httpx.Response(200, json=SUBMIT_BODY))
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}/status").mock(
        return_value=httpx.Response(200, json={"status": "PROCESSING"}),
    )

    job = client.submit_async(SLUG)
    with pytest.raises(InferenceTimeout) as exc:
        job.wait(timeout=0.05, interval=0.01)

    assert exc.value.request_id == REQ_ID
    assert exc.value.elapsed_s == pytest.approx(0.05, rel=0.5)


# ---- run_async one-shot ----------------------------------------------------


@respx.mock
def test_run_async_one_shot(client):
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(return_value=httpx.Response(200, json=SUBMIT_BODY))
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}/status").mock(
        return_value=httpx.Response(200, json={"status": "COMPLETED"})
    )
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}").mock(
        return_value=httpx.Response(200, json=RESULT_BODY)
    )

    out = client.run_async(SLUG, sleep=1, credits=1e-6, timeout=5, interval=0.01)

    assert out == RESULT_BODY


# ---- staging base_url derivation -------------------------------------------


@respx.mock
def test_v2_url_derives_from_staging_base():
    """If the caller overrides base_url for staging, v2 derives correctly."""
    staging_host = "https://api-latest.segmind.com"
    client = SegmindClient(api_key="sk-test", base_url=f"{staging_host}/v1")

    respx.post(f"{staging_host}/v2/{SLUG}").mock(
        return_value=httpx.Response(
            200,
            json={
                **SUBMIT_BODY,
                "status_url": f"{staging_host}/v2/requests/{REQ_ID}/status",
                "response_url": f"{staging_host}/v2/requests/{REQ_ID}",
            },
        ),
    )

    job = client.submit_async(SLUG)
    assert staging_host in job.status_url


# ---- module-level helpers --------------------------------------------------


@respx.mock
def test_module_level_run_async_uses_default_client():
    respx.post(f"{API_HOST}/v2/{SLUG}").mock(return_value=httpx.Response(200, json=SUBMIT_BODY))
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}/status").mock(
        return_value=httpx.Response(200, json={"status": "COMPLETED"})
    )
    respx.get(f"{API_HOST}/v2/requests/{REQ_ID}").mock(
        return_value=httpx.Response(200, json=RESULT_BODY)
    )

    with patch.dict(os.environ, {"SEGMIND_API_KEY": "sk-test"}):
        # Reset the cached default client so it picks up the env var.
        segmind._default_client = None
        out = segmind.run_async(SLUG, sleep=1, timeout=5, interval=0.01)

    assert out == RESULT_BODY


# ---- module exports --------------------------------------------------------


def test_module_exports_v2_symbols():
    assert hasattr(segmind, "submit_async")
    assert hasattr(segmind, "run_async")
    assert hasattr(segmind, "AsyncJob")
    assert hasattr(segmind, "InferenceFailed")
    assert hasattr(segmind, "InferenceTimeout")
    assert "submit_async" in segmind.__all__
    assert "run_async" in segmind.__all__
