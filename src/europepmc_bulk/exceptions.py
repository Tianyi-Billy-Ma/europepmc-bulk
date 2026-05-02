"""Exception hierarchy for europepmc-bulk."""

from __future__ import annotations


class EuropePMCBulkError(Exception):
    """Base class for all europepmc-bulk errors."""


class HTTPRetryError(EuropePMCBulkError):
    """Raised when an HTTP request fails after exhausting retries."""

    def __init__(self, url: str, attempts: int, last_status: int | None = None) -> None:
        self.url = url
        self.attempts = attempts
        self.last_status = last_status
        msg = f"HTTP request to {url} failed after {attempts} attempts"
        if last_status:
            msg += f" (last status: {last_status})"
        super().__init__(msg)


class InvalidQueryError(EuropePMCBulkError):
    """Raised when a search query or parameter is malformed."""


class StateCorruptError(EuropePMCBulkError):
    """Raised when the resume state file cannot be parsed."""
