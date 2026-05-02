"""Exponential backoff helper."""

from __future__ import annotations


def backoff_seconds(attempt: int, base: float = 5.0, cap: float = 120.0) -> float:
    """Return ``min(cap, base * 2**attempt)`` seconds."""
    return float(min(cap, base * (2**attempt)))
