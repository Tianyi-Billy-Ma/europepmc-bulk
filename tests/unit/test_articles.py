"""Tests for ArticlesClient (per-article endpoints)."""

from __future__ import annotations

import responses

from europepmc_bulk.api.articles import ArticlesClient
from europepmc_bulk.config import Config


@responses.activate
def test_get_full_text_xml() -> None:
    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC1234/fullTextXML",
        body="<article>hello</article>",
        status=200,
    )
    cfg = Config(rest_rate_limit=100)
    c = ArticlesClient(cfg)
    assert "<article>" in c.get_full_text_xml("PMC1234")


@responses.activate
def test_get_database_links() -> None:
    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/europepmc/webservices/rest/MED/12345/databaseLinks",
        json={"dbCrossReferenceList": {"dbCrossReference": [{"dbName": "PDB"}]}},
        status=200,
    )
    cfg = Config(rest_rate_limit=100)
    c = ArticlesClient(cfg)
    links = c.get_database_links("MED", "12345")
    assert links[0]["dbName"] == "PDB"
