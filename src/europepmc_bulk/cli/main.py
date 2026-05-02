"""europepmc-bulk command-line interface."""

from __future__ import annotations

from pathlib import Path

import click

from europepmc_bulk._version import __version__
from europepmc_bulk.api import (
    AbstractHarvester,
    AnnotationsCollector,
    FTPDownloader,
    OAIUpdater,
)
from europepmc_bulk.config import Config


def _config(data_dir: str | None) -> Config:
    cfg = Config(base_dir=Path(data_dir)) if data_dir else Config.from_env()
    cfg.ensure_dirs()
    return cfg


@click.group()
def cli() -> None:
    """europepmc-bulk: bulk harvest of the Europe PMC corpus."""


@cli.command("version")
def version_cmd() -> None:
    """Print the package version."""
    click.echo(f"europepmc-bulk {__version__}")


@cli.command("harvest-abstracts")
@click.option("--data-dir", default=None, envvar="EUROPEPMC_DATA_DIR")
@click.option("--start-year", type=int, default=1900, show_default=True)
@click.option("--end-year", type=int, default=2026, show_default=True)
@click.option("--format", "fmt", default="json", show_default=True, help="Comma-separated: json,xml")
@click.option("--workers", type=int, default=None)
def harvest_abstracts(data_dir: str | None, start_year: int, end_year: int, fmt: str, workers: int | None) -> None:
    """Harvest abstracts via REST search for a year range."""
    cfg = _config(data_dir)
    formats = [f.strip() for f in fmt.split(",") if f.strip()]
    h = AbstractHarvester(cfg)
    h.harvest_years(start_year, end_year, formats=formats, max_workers=workers)


@cli.command("download-fulltext")
@click.option("--data-dir", default=None, envvar="EUROPEPMC_DATA_DIR")
def download_fulltext(data_dir: str | None) -> None:
    """Download all OA full-text XML archives via FTP/HTTPS."""
    cfg = _config(data_dir)
    d = FTPDownloader(cfg)
    base = cfg.ftp_base_url.rstrip("/") + "/oa/"
    files = [f for f in d.list_directory(base) if f.endswith(".xml.gz")]
    d.download_files(base, files, cfg.fulltext_xml_dir)


@cli.command("download-annotations")
@click.option("--data-dir", default=None, envvar="EUROPEPMC_DATA_DIR")
@click.option("--ids-file", required=True, type=click.Path(exists=True, dir_okay=False))
@click.option("--type", "ann_type", default=None, help="Optional annotation type filter")
@click.option("--workers", type=int, default=None)
def download_annotations(data_dir: str | None, ids_file: str, ann_type: str | None, workers: int | None) -> None:
    """Collect semantic annotations for a list of article IDs (one per line)."""
    cfg = _config(data_dir)
    ids = [line.strip() for line in Path(ids_file).read_text().splitlines() if line.strip()]
    coll = AnnotationsCollector(cfg)
    coll.collect(ids, output_dir=cfg.annotations_dir, annotation_type=ann_type, max_workers=workers)


@cli.command("update")
@click.option("--data-dir", default=None, envvar="EUROPEPMC_DATA_DIR")
@click.option("--from-date", default=None, metavar="YYYY-MM-DD")
def update_cmd(data_dir: str | None, from_date: str | None) -> None:
    """OAI-PMH incremental update."""
    cfg = _config(data_dir)
    OAIUpdater(cfg).harvest(from_date=from_date)
