"""Per-article Europe PMC endpoints (full text, references, citations, db links)."""

from __future__ import annotations

from typing import Any, cast

from europepmc_bulk.client import HTTPClient
from europepmc_bulk.config import Config
from europepmc_bulk.utils import RateLimiter, setup_logger


class ArticlesClient:
    """Fetch per-article data from Europe PMC REST."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = setup_logger("articles_client", log_dir=config.logs_dir)
        self.rate_limiter = RateLimiter(config.rest_rate_limit)
        self.client = HTTPClient(
            timeout=config.request_timeout,
            rate_limiter=self.rate_limiter,
            logger=self.logger,
        )

    def get_full_text_xml(self, pmcid: str) -> str:
        """Return JATS XML for an open-access article."""
        url = f"{self.config.rest_base_url}/{pmcid}/fullTextXML"
        return self.client.fetch_text(url)

    def get_database_links(self, source: str, ext_id: str) -> list[dict[str, Any]]:
        """Return cross-references to external databases (PDB, UniProt, etc.)."""
        url = f"{self.config.rest_base_url}/{source}/{ext_id}/databaseLinks"
        data = self.client.fetch_json(url, params={"format": "json", "page": 1, "pageSize": 1000})
        return cast(
            "list[dict[str, Any]]", data.get("dbCrossReferenceList", {}).get("dbCrossReference", [])
        )

    def get_references(self, source: str, ext_id: str) -> list[dict[str, Any]]:
        """Return the article's references."""
        url = f"{self.config.rest_base_url}/{source}/{ext_id}/references"
        data = self.client.fetch_json(url, params={"format": "json", "page": 1, "pageSize": 1000})
        return cast("list[dict[str, Any]]", data.get("referenceList", {}).get("reference", []))

    def get_citations(self, source: str, ext_id: str) -> list[dict[str, Any]]:
        """Return papers that cite this one."""
        url = f"{self.config.rest_base_url}/{source}/{ext_id}/citations"
        data = self.client.fetch_json(url, params={"format": "json", "page": 1, "pageSize": 1000})
        return cast("list[dict[str, Any]]", data.get("citationList", {}).get("citation", []))
