"""Hits the real Europe PMC API for a single known article."""

import pytest

from europepmc_bulk import ArticlesClient, Config


@pytest.mark.live
def test_get_full_text_xml_for_known_pmcid() -> None:
    cfg = Config(rest_rate_limit=2.0)
    c = ArticlesClient(cfg)
    # PMC1234567 — known small open-access article
    xml = c.get_full_text_xml("PMC1234567")
    assert "<article" in xml
