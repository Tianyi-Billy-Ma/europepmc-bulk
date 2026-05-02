"""Shared pytest fixtures."""

from pathlib import Path

import pytest


@pytest.fixture
def tmp_state_file(tmp_path: Path) -> Path:
    """Provide a temporary state file path."""
    return tmp_path / "state.json"
