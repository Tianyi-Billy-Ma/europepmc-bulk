"""Tests for JATS XML parser."""

from __future__ import annotations

from pathlib import Path

from europepmc_bulk.parsing.jats import parse_jats_article

FIXTURE = Path(__file__).parent.parent / "fixtures" / "jats_article.xml"


def test_parse_extracts_metadata_and_sections() -> None:
    xml = FIXTURE.read_text()
    result = parse_jats_article(xml)

    assert result["pmid"] == "12345"
    assert result["pmcid"] == "PMC1234567"
    assert result["doi"] == "10.1234/example"
    assert result["title"] == "Example Title"
    assert result["abstract"] == "Example abstract."
    assert len(result["sections"]) == 2
    assert result["sections"][0]["title"] == "Introduction"
    assert "Intro paragraph" in result["sections"][0]["text"]
