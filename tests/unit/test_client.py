"""Tests for HTTPClient: retry/backoff, rate limit, JSON/XML helpers."""

from __future__ import annotations

import responses

from europepmc_bulk.client import HTTPClient
from europepmc_bulk.exceptions import HTTPRetryError
from europepmc_bulk.utils.rate_limit import RateLimiter


@responses.activate
def test_fetch_json_success() -> None:
    responses.add(
        responses.GET,
        "https://api.example.com/x",
        json={"hello": "world"},
        status=200,
    )
    client = HTTPClient()
    assert client.fetch_json("https://api.example.com/x") == {"hello": "world"}


@responses.activate
def test_fetch_json_retries_on_500_then_succeeds() -> None:
    url = "https://api.example.com/x"
    responses.add(responses.GET, url, status=500)
    responses.add(responses.GET, url, status=503)
    responses.add(responses.GET, url, json={"ok": True}, status=200)

    client = HTTPClient(retry_max=5, retry_initial_wait=0)
    assert client.fetch_json(url) == {"ok": True}
    assert len(responses.calls) == 3


@responses.activate
def test_fetch_json_raises_after_max_retries() -> None:
    url = "https://api.example.com/x"
    for _ in range(6):
        responses.add(responses.GET, url, status=503)

    client = HTTPClient(retry_max=3, retry_initial_wait=0)
    try:
        client.fetch_json(url)
        raise AssertionError("expected HTTPRetryError")
    except HTTPRetryError as e:
        assert e.url == url
        assert e.attempts == 4  # initial + 3 retries


@responses.activate
def test_fetch_json_no_retry_on_400() -> None:
    url = "https://api.example.com/x"
    responses.add(responses.GET, url, status=400, json={"err": "bad"})

    client = HTTPClient(retry_max=3, retry_initial_wait=0)
    try:
        client.fetch_json(url)
        raise AssertionError("expected HTTPRetryError")
    except HTTPRetryError as e:
        assert e.attempts == 1


@responses.activate
def test_rate_limiter_invoked() -> None:
    """If a rate limiter is passed in, every request goes through it."""
    url = "https://api.example.com/x"
    responses.add(responses.GET, url, json={"ok": True}, status=200)
    responses.add(responses.GET, url, json={"ok": True}, status=200)

    calls: list[None] = []

    class CountingLimiter(RateLimiter):
        def wait(self) -> None:
            calls.append(None)

    client = HTTPClient(rate_limiter=CountingLimiter(rate=100.0))
    client.fetch_json(url)
    client.fetch_json(url)
    assert len(calls) == 2
