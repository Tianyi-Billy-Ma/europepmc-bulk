"""Tests for AbstractHarvester (REST search + cursor pagination)."""

from __future__ import annotations

import json
from pathlib import Path

import responses

from europepmc_bulk.api.search import AbstractHarvester
from europepmc_bulk.config import Config

FIXTURES = Path(__file__).parent.parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


@responses.activate
def test_get_total_count(tmp_path: Path) -> None:
    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        json={"hitCount": 42},
        status=200,
    )
    cfg = Config(base_dir=tmp_path, rest_rate_limit=100)
    h = AbstractHarvester(cfg)
    assert h.get_total_count("supramolecular") == 42


@responses.activate
def test_harvest_year_writes_pages_and_clears_cursor(tmp_path: Path) -> None:
    cfg = Config(base_dir=tmp_path, rest_rate_limit=100)
    cfg.ensure_dirs()

    page1 = _load("search_response_page1.json")
    page2 = _load("search_response_page2.json")
    page2["nextCursorMark"] = page1["nextCursorMark"]  # same cursor → terminates

    # Hit count call (resultType=lite)
    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        json={"hitCount": 2},
    )
    # Page 1
    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        json=page1,
    )
    # Page 2 (same cursor → end)
    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/europepmc/webservices/rest/search",
        json=page2,
    )

    h = AbstractHarvester(cfg)
    h.harvest_year(2024, output_format="json")

    out_dir = cfg.abstracts_json_dir / "2024"
    files = sorted(out_dir.glob("page_*.json"))
    assert len(files) == 2
    assert json.loads(files[0].read_text())["resultList"]["result"][0]["pmid"] == "1001"
