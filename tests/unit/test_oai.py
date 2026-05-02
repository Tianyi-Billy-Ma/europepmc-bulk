"""Tests for OAIUpdater (OAI-PMH incremental harvest)."""

from __future__ import annotations

from pathlib import Path

from europepmc_bulk.api.oai import OAIUpdater
from europepmc_bulk.config import Config

FIXTURE = Path(__file__).parent.parent / "fixtures" / "oai_response.xml"


def test_extract_resumption_token() -> None:
    cfg = Config(rest_rate_limit=100)
    u = OAIUpdater(cfg)
    text = FIXTURE.read_text()
    assert u._extract_resumption_token(text) == "nexttoken"


def test_extract_resumption_token_returns_empty_when_absent() -> None:
    cfg = Config(rest_rate_limit=100)
    u = OAIUpdater(cfg)
    assert u._extract_resumption_token("<OAI-PMH></OAI-PMH>") == ""
