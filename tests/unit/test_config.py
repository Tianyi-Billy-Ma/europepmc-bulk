"""Tests for Config dataclass."""

from pathlib import Path

import pytest

from europepmc_bulk.config import Config


def test_default_values() -> None:
    cfg = Config()
    assert cfg.rest_base_url == "https://www.ebi.ac.uk/europepmc/webservices/rest"
    assert cfg.rest_rate_limit == 10.0
    assert cfg.annotations_batch_size == 8
    assert cfg.request_timeout == 60


def test_base_dir_overrides_subdirs(tmp_path: Path) -> None:
    cfg = Config(base_dir=tmp_path)
    assert cfg.abstracts_json_dir == tmp_path / "abstracts" / "json"
    assert cfg.fulltext_xml_dir == tmp_path / "fulltext" / "xml"
    assert cfg.state_dir == tmp_path / ".state"


def test_ensure_dirs_creates_all(tmp_path: Path) -> None:
    cfg = Config(base_dir=tmp_path)
    cfg.ensure_dirs()
    assert cfg.abstracts_json_dir.is_dir()
    assert cfg.fulltext_xml_dir.is_dir()
    assert cfg.state_dir.is_dir()
    assert cfg.logs_dir.is_dir()


def test_from_env_loads_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EUROPEPMC_DATA_DIR", str(tmp_path))
    cfg = Config.from_env()
    assert cfg.base_dir == tmp_path


def test_invalid_rate_limit_raises() -> None:
    with pytest.raises(ValueError):
        Config(rest_rate_limit=0)
