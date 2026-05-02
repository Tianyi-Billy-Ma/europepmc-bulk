"""Tests for the exception hierarchy."""

from europepmc_bulk.exceptions import (
    EuropePMCBulkError,
    HTTPRetryError,
    InvalidQueryError,
    StateCorruptError,
)


def test_all_exceptions_inherit_base() -> None:
    for exc in (HTTPRetryError, InvalidQueryError, StateCorruptError):
        assert issubclass(exc, EuropePMCBulkError)


def test_http_retry_error_carries_attempts_and_url() -> None:
    err = HTTPRetryError(url="https://example.com", attempts=5)
    assert err.url == "https://example.com"
    assert err.attempts == 5
    assert "5" in str(err)
