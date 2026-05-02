"""Tests for FTPDownloader (HTTPS-mirror bulk downloader)."""

from __future__ import annotations

from pathlib import Path

import responses

from europepmc_bulk.api.ftp import FTPDownloader, parse_directory_listing
from europepmc_bulk.config import Config

FIXTURE = Path(__file__).parent.parent / "fixtures" / "ftp_listing.html"


def test_parse_directory_listing_filters_parent_and_query() -> None:
    html = FIXTURE.read_text()
    files = parse_directory_listing(html)
    assert "archive_001.xml.gz" in files
    assert "archive_002.xml.gz" in files
    assert "readme.txt" in files
    assert "?C=N" not in files
    assert "../" not in files


@responses.activate
def test_download_file_writes_to_dest(tmp_path: Path) -> None:
    responses.add(
        responses.GET,
        "https://example.com/archive.xml.gz",
        body=b"compressed bytes",
        status=200,
    )
    cfg = Config(base_dir=tmp_path)
    cfg.ensure_dirs()
    d = FTPDownloader(cfg)
    dest = tmp_path / "archive.xml.gz"
    d.download_file("https://example.com/archive.xml.gz", dest)
    assert dest.read_bytes() == b"compressed bytes"


@responses.activate
def test_list_directory(tmp_path: Path) -> None:
    responses.add(
        responses.GET,
        "https://ftp.ebi.ac.uk/pub/databases/pmc/oa/",
        body=FIXTURE.read_text(),
        status=200,
    )
    cfg = Config(base_dir=tmp_path)
    d = FTPDownloader(cfg)
    files = d.list_directory("https://ftp.ebi.ac.uk/pub/databases/pmc/oa/")
    assert "archive_001.xml.gz" in files
