"""OAI-PMH incremental harvester for Europe PMC."""

from __future__ import annotations

import re

from europepmc_bulk.client import HTTPClient
from europepmc_bulk.config import Config
from europepmc_bulk.persistence import ResumeState, atomic_write
from europepmc_bulk.utils import RateLimiter, setup_logger

_TOKEN_RE = re.compile(
    r"<resumptionToken[^>]*>([^<]*)</resumptionToken>", re.IGNORECASE | re.DOTALL
)


class OAIUpdater:
    """Incremental harvester via OAI-PMH ListRecords with resumption tokens."""

    def __init__(self, config: Config, rate: float = 2.0) -> None:
        self.config = config
        self.logger = setup_logger("oai_updater", log_dir=config.logs_dir)
        self.rate_limiter = RateLimiter(rate)
        self.resume_state = ResumeState(config.state_dir / "oai_updater.json")
        self.client = HTTPClient(
            timeout=config.request_timeout,
            rate_limiter=self.rate_limiter,
            logger=self.logger,
        )

    @staticmethod
    def _extract_resumption_token(xml: str) -> str:
        m = _TOKEN_RE.search(xml)
        return m.group(1).strip() if m else ""

    def harvest(
        self,
        oai_set: str = "pmc-open",
        metadata_prefix: str = "pmc",
        from_date: str | None = None,
    ) -> None:
        """Download all OAI records since ``from_date``, with resumption."""
        out_dir = self.config.base_dir / "updates" / oai_set
        out_dir.mkdir(parents=True, exist_ok=True)

        token_key = f"oai_{oai_set}_token"
        page_key = f"oai_{oai_set}_page"
        token = self.resume_state.get(token_key)
        page = self.resume_state.get(page_key, 0)

        while True:
            params: dict[str, object] = {"verb": "ListRecords"}
            if token:
                params["resumptionToken"] = token
            else:
                params["set"] = oai_set
                params["metadataPrefix"] = metadata_prefix
                if from_date:
                    params["from"] = from_date

            xml = self.client.fetch_text(self.config.oai_base_url, params=params)
            atomic_write(out_dir / f"page_{page:06d}.xml", xml)
            page += 1

            next_token = self._extract_resumption_token(xml)
            if not next_token:
                self.logger.info("OAI harvest complete (%d pages)", page)
                self.resume_state.remove(token_key)
                self.resume_state.remove(page_key)
                return

            token = next_token
            self.resume_state.set(token_key, token)
            self.resume_state.set(page_key, page)
