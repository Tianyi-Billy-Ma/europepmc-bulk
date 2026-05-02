"""Hits the real Europe PMC API. Marked @live; deselect with -m 'not live'."""

from pathlib import Path

import pytest

from europepmc_bulk import AbstractHarvester, Config


@pytest.mark.live
def test_get_total_count_returns_positive_number(tmp_path: Path) -> None:
    cfg = Config(base_dir=tmp_path, rest_rate_limit=2.0)
    h = AbstractHarvester(cfg)
    n = h.get_total_count("supramolecular")
    assert n > 1000


@pytest.mark.live
def test_harvest_one_year_writes_pages(tmp_path: Path) -> None:
    cfg = Config(base_dir=tmp_path, rest_rate_limit=2.0, rest_page_size=10)
    cfg.ensure_dirs()
    h = AbstractHarvester(cfg)
    # Use 1900 — has very few articles, finishes quickly
    h.harvest_year(1900, output_format="json")
    out = list((cfg.abstracts_json_dir / "1900").glob("page_*.json"))
    assert len(out) >= 1
