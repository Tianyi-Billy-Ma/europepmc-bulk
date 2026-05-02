"""Bulk download from Europe PMC's FTP/HTTPS mirror."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests
from tqdm import tqdm

from europepmc_bulk.config import Config
from europepmc_bulk.persistence import ResumeState
from europepmc_bulk.utils import setup_logger

_HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)


def parse_directory_listing(html: str) -> list[str]:
    """Return filenames listed in an Apache-style HTML directory listing."""
    hrefs = _HREF_RE.findall(html)
    return [h for h in hrefs if h and not h.startswith(("?", "/", "http", ".."))]


class FTPDownloader:
    """Download bulk archives from the Europe PMC FTP/HTTPS mirror."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.logger = setup_logger("ftp_downloader", log_dir=config.logs_dir)
        self.resume_state = ResumeState(config.state_dir / "ftp_downloader.json")

    def list_directory(self, url: str) -> list[str]:
        """Fetch and parse a directory listing."""
        resp = requests.get(url, timeout=self.config.request_timeout)
        resp.raise_for_status()
        return parse_directory_listing(resp.text)

    def download_file(
        self,
        url: str,
        dest: Path,
        resume: bool = True,
        chunk_size: int = 8192,
    ) -> Path:
        """Stream-download ``url`` to ``dest``, with HTTP Range resume support."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        headers: dict[str, str] = {}
        mode = "wb"
        if resume and dest.exists():
            existing = dest.stat().st_size
            if existing > 0:
                headers["Range"] = f"bytes={existing}-"
                mode = "ab"
        resp = requests.get(url, headers=headers, stream=True, timeout=self.config.download_timeout)
        if resp.status_code == 416:
            return dest
        if resp.status_code not in (200, 206):
            resp.raise_for_status()
        if resp.status_code == 200:
            mode = "wb"
        with open(dest, mode) as f:
            for chunk in resp.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
        return dest

    def download_files(
        self,
        base_url: str,
        filenames: list[str],
        dest_dir: Path,
        max_workers: int | None = None,
    ) -> None:
        dest_dir.mkdir(parents=True, exist_ok=True)
        max_workers = max_workers or self.config.max_concurrent_downloads

        def _one(filename: str) -> str:
            url = base_url.rstrip("/") + "/" + filename
            dest = dest_dir / filename
            self.download_file(url, dest)
            self.resume_state.set(filename, str(dest))
            return filename

        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(_one, fn): fn for fn in filenames}
            with tqdm(total=len(filenames), desc="ftp", unit="file") as pbar:
                for f in as_completed(futures):
                    try:
                        f.result()
                    except Exception as exc:
                        self.logger.error("Failed: %s", exc)
                    pbar.update(1)
