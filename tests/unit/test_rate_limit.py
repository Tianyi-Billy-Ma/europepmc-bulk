"""Tests for the token-bucket rate limiter."""

import threading
import time

from europepmc_bulk.utils.rate_limit import RateLimiter


def test_rate_limiter_first_call_immediate() -> None:
    rl = RateLimiter(rate=10.0)
    start = time.monotonic()
    rl.wait()
    assert time.monotonic() - start < 0.05


def test_rate_limiter_throttles_second_call() -> None:
    rl = RateLimiter(rate=10.0)  # 100 ms min interval
    rl.wait()
    start = time.monotonic()
    rl.wait()
    elapsed = time.monotonic() - start
    assert 0.08 <= elapsed <= 0.20


def test_rate_limiter_thread_safe() -> None:
    """5 threads x 4 requests at 50 req/s should take ~0.4 s, not parallel."""
    rl = RateLimiter(rate=50.0)
    counter = {"n": 0}
    lock = threading.Lock()

    def worker() -> None:
        for _ in range(4):
            rl.wait()
            with lock:
                counter["n"] += 1

    threads = [threading.Thread(target=worker) for _ in range(5)]
    start = time.monotonic()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.monotonic() - start

    assert counter["n"] == 20
    assert 0.3 <= elapsed <= 3.0
