"""Tests for AnnotationsCollector."""

from __future__ import annotations

import json
from pathlib import Path

import responses

from europepmc_bulk.api.annotations import AnnotationsCollector
from europepmc_bulk.config import Config

FIXTURE = Path(__file__).parent.parent / "fixtures" / "annotations_batch.json"


@responses.activate
def test_collect_writes_one_file_per_batch(tmp_path: Path) -> None:
    cfg = Config(base_dir=tmp_path, rest_rate_limit=100, annotations_batch_size=2)
    cfg.ensure_dirs()

    body = json.loads(FIXTURE.read_text())
    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds",
        json=body,
        status=200,
    )

    coll = AnnotationsCollector(cfg)
    article_ids = ["MED:1001", "MED:1002", "MED:1003", "MED:1004"]
    coll.collect(article_ids, output_dir=cfg.annotations_dir)

    batch_files = sorted(cfg.annotations_dir.glob("batch_*.json"))
    assert len(batch_files) == 2


@responses.activate
def test_collect_resumes_skips_existing(tmp_path: Path) -> None:
    cfg = Config(base_dir=tmp_path, rest_rate_limit=100, annotations_batch_size=2)
    cfg.ensure_dirs()

    body = json.loads(FIXTURE.read_text())
    pre = cfg.annotations_dir / "batch_000000.json"
    pre.write_text(json.dumps(body))
    responses.add(
        responses.GET,
        "https://www.ebi.ac.uk/europepmc/annotations_api/annotationsByArticleIds",
        json=body,
        status=200,
    )

    coll = AnnotationsCollector(cfg)
    coll.collect(["MED:1001", "MED:1002", "MED:1003", "MED:1004"], output_dir=cfg.annotations_dir)
    assert len(responses.calls) == 1  # only batch 1 hit network
