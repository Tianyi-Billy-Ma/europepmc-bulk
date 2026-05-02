"""Europe PMC REST search with cursor-mark pagination."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm

from europepmc_bulk.client import HTTPClient
from europepmc_bulk.config import Config
from europepmc_bulk.persistence import ResumeState, atomic_write
from europepmc_bulk.utils import RateLimiter, setup_logger


class AbstractHarvester:
    """Harvest abstracts via the Europe PMC REST search endpoint.

    Uses ``cursorMark`` pagination so harvesting a year is deterministic and
    resumable. Results are stored as one file per page under
    ``config.abstracts_json_dir/{year}/page_{N:06d}.json`` (or
    ``abstracts_xml_dir`` when ``output_format='xml'``).
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = setup_logger("abstract_harvester", log_dir=config.logs_dir)
        self.rate_limiter = RateLimiter(config.rest_rate_limit)
        self.resume_state = ResumeState(config.state_dir / "abstract_harvester.json")
        self.client = HTTPClient(
            timeout=config.request_timeout,
            rate_limiter=self.rate_limiter,
            logger=self.logger,
        )

    def get_total_count(self, query: str) -> int:
        url = f"{self.config.rest_base_url}/search"
        data = self.client.fetch_json(
            url,
            params={
                "query": query,
                "resultType": "lite",
                "format": "json",
                "pageSize": 1,
                "cursorMark": "*",
            },
        )
        return int(data.get("hitCount", 0))

    def harvest_year(self, year: int, output_format: str = "json") -> None:
        if output_format not in ("json", "xml"):
            raise ValueError("output_format must be 'json' or 'xml'")

        query = f"FIRST_PDATE:[{year}-01-01 TO {year}-12-31]"
        cursor_key = f"abstracts_{year}_{output_format}_cursor"
        page_key = f"abstracts_{year}_{output_format}_page"

        out_dir = (
            self.config.abstracts_xml_dir
            if output_format == "xml"
            else self.config.abstracts_json_dir
        ) / str(year)
        out_dir.mkdir(parents=True, exist_ok=True)

        cursor = self.resume_state.get(cursor_key, "*")
        page = self.resume_state.get(page_key, 0)
        total_hits = self.get_total_count(query)
        pages_estimate = max(1, total_hits // self.config.rest_page_size + 1)

        url = f"{self.config.rest_base_url}/search"
        with tqdm(
            total=pages_estimate, initial=page, desc=f"{year}/{output_format}", unit="page"
        ) as pbar:
            while True:
                params = {
                    "query": query,
                    "resultType": "core",
                    "format": output_format,
                    "pageSize": self.config.rest_page_size,
                    "cursorMark": cursor,
                }
                if output_format == "xml":
                    text = self.client.fetch_text(url, params=params)
                    out_file = out_dir / f"page_{page:06d}.xml"
                    atomic_write(out_file, text)
                    next_cursor = _extract_xml_cursor(text)
                else:
                    data = self.client.fetch_json(url, params=params)
                    out_file = out_dir / f"page_{page:06d}.json"
                    atomic_write(out_file, json.dumps(data))
                    next_cursor = data.get("nextCursorMark", "")

                page += 1
                pbar.update(1)

                if not next_cursor or next_cursor == cursor:
                    self.logger.info(
                        "Year %d [%s]: finished after %d pages", year, output_format, page
                    )
                    self.resume_state.remove(cursor_key)
                    self.resume_state.remove(page_key)
                    return

                cursor = next_cursor
                self.resume_state.set(cursor_key, cursor)
                self.resume_state.set(page_key, page)

    def harvest_years(
        self,
        start_year: int,
        end_year: int,
        formats: list[str] | None = None,
        max_workers: int | None = None,
    ) -> None:
        formats = formats or ["json"]
        max_workers = max_workers or self.config.max_concurrent_api_requests

        tasks = [(y, f) for y in range(start_year, end_year + 1) for f in formats]
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(self.harvest_year, y, f): (y, f) for y, f in tasks}
            for future in as_completed(futures):
                y, f = futures[future]
                try:
                    future.result()
                except Exception:
                    self.logger.exception("Error harvesting year=%d format=%s", y, f)


def _extract_xml_cursor(xml_text: str) -> str:
    open_tag = "<nextCursorMark>"
    close_tag = "</nextCursorMark>"
    start = xml_text.find(open_tag)
    if start == -1:
        return ""
    start += len(open_tag)
    end = xml_text.find(close_tag, start)
    if end == -1:
        return ""
    return xml_text[start:end]
