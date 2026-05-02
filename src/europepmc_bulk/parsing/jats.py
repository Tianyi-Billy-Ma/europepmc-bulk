"""Parse a single JATS XML article into a flat dict."""

from __future__ import annotations

from typing import Any

from lxml import etree  # type: ignore[import-untyped]


def parse_jats_article(xml: str) -> dict[str, Any]:
    """Extract identifiers, title, abstract, and section text from JATS XML.

    Returns a dict with keys: ``pmid``, ``pmcid``, ``doi``, ``title``,
    ``abstract``, ``sections`` (list of ``{"title", "text"}``).
    """
    root = etree.fromstring(xml.encode("utf-8"))

    def _id(pub_id_type: str) -> str:
        el = root.find(f".//article-id[@pub-id-type='{pub_id_type}']")
        return el.text.strip() if el is not None and el.text else ""

    def _text_of(el: etree._Element | None) -> str:
        return " ".join(t.strip() for t in el.itertext()).strip() if el is not None else ""

    title_el = root.find(".//article-meta//article-title")
    abstract_el = root.find(".//article-meta//abstract")

    sections: list[dict[str, str]] = []
    for sec in root.findall(".//body//sec"):
        sec_title_el = sec.find("title")
        sec_title = sec_title_el.text.strip() if sec_title_el is not None and sec_title_el.text else ""
        sec_text_parts = [_text_of(p) for p in sec.findall("p")]
        sections.append({"title": sec_title, "text": " ".join(sec_text_parts)})

    return {
        "pmid": _id("pmid"),
        "pmcid": _id("pmcid"),
        "doi": _id("doi"),
        "title": _text_of(title_el),
        "abstract": _text_of(abstract_el),
        "sections": sections,
    }
