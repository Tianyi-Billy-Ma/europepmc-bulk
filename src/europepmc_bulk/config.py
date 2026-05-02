"""Configuration dataclass for europepmc-bulk."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def _default_base_dir() -> Path:
    return Path(os.environ.get("EUROPEPMC_DATA_DIR", "./europepmc-data"))


@dataclass
class Config:
    """Configuration for harvest jobs.

    All paths under ``base_dir`` follow a fixed layout. To change a single
    subdirectory, set ``base_dir`` and override the property.
    """

    base_dir: Path = field(default_factory=_default_base_dir)

    # REST API
    rest_base_url: str = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    rest_page_size: int = 1000
    rest_rate_limit: float = 10.0  # requests per second

    # Annotations API
    annotations_base_url: str = "https://www.ebi.ac.uk/europepmc/annotations_api"
    annotations_batch_size: int = 8  # API rejects batches of 9+

    # OAI-PMH
    oai_base_url: str = "https://europepmc.org/oai.cgi"

    # FTP (via HTTPS mirror)
    ftp_base_url: str = "https://ftp.ebi.ac.uk/pub/databases/pmc"

    # Timeouts
    request_timeout: int = 60
    download_timeout: int = 600

    # Concurrency
    max_concurrent_downloads: int = 4
    max_concurrent_api_requests: int = 5

    def __post_init__(self) -> None:
        if self.rest_rate_limit <= 0:
            raise ValueError("rest_rate_limit must be positive")
        if self.annotations_batch_size <= 0 or self.annotations_batch_size > 8:
            raise ValueError("annotations_batch_size must be in (0, 8]")
        self.base_dir = Path(self.base_dir)

    @property
    def abstracts_json_dir(self) -> Path:
        return self.base_dir / "abstracts" / "json"

    @property
    def abstracts_xml_dir(self) -> Path:
        return self.base_dir / "abstracts" / "xml"

    @property
    def fulltext_xml_dir(self) -> Path:
        return self.base_dir / "fulltext" / "xml"

    @property
    def fulltext_json_dir(self) -> Path:
        return self.base_dir / "fulltext" / "json"

    @property
    def annotations_dir(self) -> Path:
        return self.base_dir / "annotations" / "semantic"

    @property
    def textmined_dir(self) -> Path:
        return self.base_dir / "annotations" / "text_mined"

    @property
    def metadata_dir(self) -> Path:
        return self.base_dir / "metadata"

    @property
    def logs_dir(self) -> Path:
        return self.base_dir / "logs"

    @property
    def state_dir(self) -> Path:
        return self.base_dir / ".state"

    def ensure_dirs(self) -> None:
        for d in [
            self.abstracts_json_dir,
            self.abstracts_xml_dir,
            self.fulltext_xml_dir,
            self.fulltext_json_dir,
            self.annotations_dir,
            self.textmined_dir,
            self.metadata_dir,
            self.logs_dir,
            self.state_dir,
        ]:
            d.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> Config:
        """Construct a Config from environment variables (currently only EUROPEPMC_DATA_DIR)."""
        return cls(base_dir=_default_base_dir())
