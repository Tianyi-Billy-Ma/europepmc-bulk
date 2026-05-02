"""Synchronous HTTP client with retry/backoff and optional rate limiting."""

from __future__ import annotations

import logging
import time
from typing import Any

import requests

from europepmc_bulk.exceptions import HTTPRetryError
from europepmc_bulk.utils.rate_limit import RateLimiter
from europepmc_bulk.utils.retry import backoff_seconds

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class HTTPClient:
    """GET-only HTTP client with retry, backoff, and pluggable rate limiter."""

    def __init__(
        self,
        timeout: int = 60,
        retry_max: int = 5,
        retry_initial_wait: float = 5.0,
        retry_cap_wait: float = 120.0,
        rate_limiter: RateLimiter | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.timeout = timeout
        self.retry_max = retry_max
        self.retry_initial_wait = retry_initial_wait
        self.retry_cap_wait = retry_cap_wait
        self.rate_limiter = rate_limiter
        self.logger = logger or logging.getLogger("europepmc_bulk")
        self._session = requests.Session()

    def _request_with_retry(self, url: str, params: dict[str, Any] | None) -> requests.Response:
        for attempt in range(self.retry_max + 1):
            if self.rate_limiter is not None:
                self.rate_limiter.wait()
            resp = self._session.get(url, params=params, timeout=self.timeout)
            if resp.status_code in _RETRYABLE_STATUS and attempt < self.retry_max:
                wait = backoff_seconds(attempt, base=self.retry_initial_wait, cap=self.retry_cap_wait)
                self.logger.warning(
                    "HTTP %d for %s — retry %d/%d in %.1fs",
                    resp.status_code, url, attempt + 1, self.retry_max, wait,
                )
                if wait > 0:
                    time.sleep(wait)
                continue
            if not resp.ok:
                raise HTTPRetryError(url=url, attempts=attempt + 1, last_status=resp.status_code)
            return resp
        raise HTTPRetryError(url=url, attempts=self.retry_max + 1)

    def fetch_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        return self._request_with_retry(url, params).json()

    def fetch_text(self, url: str, params: dict[str, Any] | None = None) -> str:
        return self._request_with_retry(url, params).text
