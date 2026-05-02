"""Europe PMC Annotations API batch collector."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from tqdm import tqdm

from europepmc_bulk.client import HTTPClient
from europepmc_bulk.config import Config
from europepmc_bulk.persistence import ResumeState, atomic_write
from europepmc_bulk.utils import RateLimiter, setup_logger


class AnnotationsCollector:
    """Collect semantic annotations in batches from the Annotations API.

    Each batch results in one JSON file ``batch_NNNNNN.json``. The collector
    skips any batch file that already exists, so re-running is idempotent.
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = setup_logger("annotations_collector", log_dir=config.logs_dir)
        self.rate_limiter = RateLimiter(config.rest_rate_limit)
        self.resume_state = ResumeState(config.state_dir / "annotations_collector.json")
        self.client = HTTPClient(
            timeout=config.request_timeout,
            rate_limiter=self.rate_limiter,
            logger=self.logger,
        )

    def _fetch_one(
        self,
        batch: list[str],
        batch_idx: int,
        out_dir: Path,
        annotation_type: str | None,
    ) -> tuple[int, bool]:
        out_file = out_dir / f"batch_{batch_idx:06d}.json"
        if out_file.exists():
            return batch_idx, True
        url = f"{self.config.annotations_base_url}/annotationsByArticleIds"
        params: dict[str, object] = {
            "articleIds": ",".join(batch),
            "format": "JSON",
        }
        if annotation_type:
            params["type"] = annotation_type
        try:
            data = self.client.fetch_json(url, params=params)
            atomic_write(out_file, json.dumps(data))
            return batch_idx, True
        except Exception as exc:
            self.logger.error("Annotation batch %d failed: %s", batch_idx, exc)
            return batch_idx, False

    def collect(
        self,
        article_ids: list[str],
        output_dir: Path,
        annotation_type: str | None = None,
        max_workers: int | None = None,
    ) -> None:
        """Collect annotations for all article IDs.

        Parameters
        ----------
        article_ids
            Identifiers in ``"MED:<pmid>"`` or ``"PMC:<pmcid>"`` format.
        output_dir
            Directory to write batch JSON files to. Created if missing.
        annotation_type
            Optional filter (e.g. ``"Chemicals"``).
        max_workers
            Concurrency. Default: ``config.max_concurrent_api_requests``.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        size = self.config.annotations_batch_size
        max_workers = max_workers or self.config.max_concurrent_api_requests

        batches = [article_ids[i : i + size] for i in range(0, len(article_ids), size)]
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {
                pool.submit(self._fetch_one, b, i, output_dir, annotation_type): i
                for i, b in enumerate(batches)
            }
            with tqdm(total=len(batches), desc="annotations", unit="batch") as pbar:
                for future in as_completed(futures):
                    future.result()
                    pbar.update(1)
