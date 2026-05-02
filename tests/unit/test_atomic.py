"""Tests for atomic file writes."""

from pathlib import Path

import pytest

from europepmc_bulk.persistence.atomic import atomic_write


def test_atomic_write_creates_file(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"
    atomic_write(target, "hello")
    assert target.read_text() == "hello"


def test_atomic_write_overwrites_existing(tmp_path: Path) -> None:
    target = tmp_path / "out.txt"
    target.write_text("old")
    atomic_write(target, "new")
    assert target.read_text() == "new"


def test_atomic_write_creates_parent_dirs(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "deep" / "out.txt"
    atomic_write(target, "hi")
    assert target.read_text() == "hi"


def test_atomic_write_no_partial_file_on_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """If the write fails midway, no partial file should remain at the target path."""
    target = tmp_path / "out.txt"
    target.write_text("preserved")

    def boom(*args: object, **kwargs: object) -> None:
        raise RuntimeError("simulated failure")

    monkeypatch.setattr("os.replace", boom)
    with pytest.raises(RuntimeError):
        atomic_write(target, "new")

    assert target.read_text() == "preserved"
    assert list(tmp_path.glob("*.tmp")) == []
