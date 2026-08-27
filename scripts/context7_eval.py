#!/usr/bin/env python3
"""Canary for what AI assistants are told about this SDK via Context7.

Asks Context7 the questions a developer would ask, then checks the served
snippets for two failure modes that have actually shipped:

* retired content — model slugs and verbs that no longer exist keep being
  served until the index is refreshed
* wrong emphasis — answers that teach a non-default verb for the task

Run it after any docs change lands (the refresh workflow triggers a
re-index; give it a few minutes) or on the weekly schedule. Exits non-zero
with a report when any check fails — which usually means the Context7 entry
needs a refresh, not that the docs regressed.
"""

import subprocess
import sys

LIBRARY = "/segmind/segmind-python"

# Content that must never appear in a served answer: slugs retired in
# production and the verb removed in 1.1.0.
FORBIDDEN = [
    "seedream-v3-text-to-image",
    "seedance-1-pro",
    "seededit-v3",
    "qwen2p5-vl-32b-instruct",
    "run_async(",
    "SD2_1",
    "Kadinsky",
]

# (question, at least one of these must appear in the answer)
QUESTIONS = [
    ("How do I generate an image with the Segmind Python SDK?", ["segmind.run(", "client.run("]),
    ("How do I generate a video that takes several minutes?", ["submit_async"]),
    ("How do I handle errors when running a model?", ["InferenceFailed", "SegmindError"]),
    ("How do I chat with an LLM using the Segmind SDK?", ["segmind.chat(", "client.chat("]),
    ("How do I upload a file and use it as a model input?", ["files.upload"]),
]


def fetch(question: str) -> str:
    result = subprocess.run(
        ["npx", "-y", "ctx7@latest", "docs", LIBRARY, question],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ctx7 failed for {question!r}: {result.stderr[:300]}")
    return result.stdout


def main() -> int:
    failures = []
    for question, expected_any in QUESTIONS:
        answer = fetch(question)
        hits = [p for p in FORBIDDEN if p in answer]
        if hits:
            failures.append(f"{question!r} serves retired content: {', '.join(hits)}")
        if not any(e in answer for e in expected_any):
            failures.append(f"{question!r} teaches none of {expected_any}")

    if failures:
        print(f"context7-eval: {len(failures)} failure(s) — the {LIBRARY} entry "
              "likely needs a refresh (context7.com admin panel or the "
              "refresh workflow):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"context7-eval: {len(QUESTIONS)} question(s) pass — no retired "
          "content, expected verbs present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
