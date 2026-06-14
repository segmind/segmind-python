# Changelog

All notable changes to the Segmind Python SDK are documented here.

## 1.1.0 — ⚠️ BREAKING

This release redefines the inference verbs to make **async the default** and
adds a normalized **LLM chat** surface. Adoption was effectively zero, so the
verb flip ships without a deprecation cycle.

### Breaking — verb redefinition (SEG-354)

| Verb | 1.1.0 behavior | Was (≤1.0.x) |
| --- | --- | --- |
| `run(slug, **params)` | **async** — v2 queue-backed, submit + poll until done; returns the result `dict` | sync v1, returned `httpx.Response` |
| `run_sync(slug, **params)` | **sync** — single blocking `POST /v1/{slug}`; returns `httpx.Response` | _new_ (this is the old `run`) |
| `run_async(slug, **params)` | **removed** — no alias; raises `AttributeError` / `ImportError` | the old async one-shot |
| `submit_async(slug, **params)` | unchanged — returns `AsyncJob` (`.wait/.status/.result`) | unchanged |
| `stream(...)` | raises `NotImplementedError` (gateway has no SSE yet) | silently returned `None` |

**Migration:**

```python
# 1.0.x  ->  1.1.0
segmind.run(slug, ...)          # sync image/etc.   ->  segmind.run_sync(slug, ...)
segmind.run_async(slug, ...)    # async one-shot     ->  segmind.run(slug, ...)
segmind.submit_async(slug, ...) # unchanged
```

`run` (async) inherits the 600s `job.wait` default. For **long / video**
models the documented path is `submit_async()` + `job.wait(timeout=…)`, not
`run`. All model params — including any literally named `timeout` / `interval`
— are still forwarded verbatim to the model body (SEG-339).

### Added — LLM chat surface + output normalization (SEG-344)

The gateway returns each provider's raw native JSON in three incompatible
shapes (OpenAI `choices[0].message.content`, Anthropic `content[0].text`,
Gemini `candidates[0].content.parts[0].text`). The new chat surface hides that:

- `chat(slug, *, messages=[...] | prompt=..., **opts)` → `ChatResponse` — **async** (mirrors `run`).
- `chat_sync(...)` → `ChatResponse` — sync single `POST /v1`.
- `submit_chat(...)` → `AsyncChatJob` (`.wait/.status/.result/.request_id`).
- `ChatResponse`: `.text` (provider-normalized), `.json()` (parse JSON-mode output), `.usage`, `.finish_reason`, `.tool_calls` (empty until the gateway forwards `tools`), `.raw` (always the native body).
- `image_url(url | local_path)` — builds an OpenAI image content-part; local paths are base64-encoded into a `data:` URI (recommended over URL, whose fetch path 400s on some hosts).
- The v2 async `output` is a **stringified** copy of the provider JSON; the async chat path `json.loads`-es it before normalizing.
- `stream=` kwarg reserved on `chat()`; raises `NotImplementedError` until the gateway grows SSE.

100% additive apart from the verb rename above.

## 1.0.2

- Export `SegmindError` at the top level; version-driven User-Agent; isolate
  `run_async` kwargs so model params named `timeout`/`interval` aren't shadowed
  (SEG-339/337/338).

## 1.0.1

- `X-Initiator: SDK-PY` header so SDK traffic is attributable in spotdb (SEG-319).

## 1.0.0

- Initial release: `run`, PixelFlows, webhooks, file upload, generations,
  models, finetune, plus the v2 async helpers (`submit_async`, `run_async`).
