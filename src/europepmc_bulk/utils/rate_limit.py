"""Thread-safe token-bucket rate limiter."""

from __future__ import annotations

import threading
import time


class RateLimiter:
    """Block until the next request slot is available.

    Implements the simplest token-bucket: minimum interval between calls.
    Thread-safe; multiple threads sharing one instance respect a global rate.

    Parameters
    ----------
    rate
        Maximum requests per second.
    """

    def __init__(self, rate: float) -> None:
        if rate <= 0:
            raise ValueError("rate must be positive")
        self.rate = rate
        self.min_interval = 1.0 / rate
        self._last = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        """Block until at least ``min_interval`` has elapsed since the last call."""
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
            self._last = time.monotonic()
