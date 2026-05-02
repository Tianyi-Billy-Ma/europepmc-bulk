"""Tests for the Click CLI surface."""

from __future__ import annotations

from click.testing import CliRunner

from europepmc_bulk.cli.main import cli


def test_cli_help_lists_subcommands() -> None:
    result = CliRunner().invoke(cli, ["--help"])
    assert result.exit_code == 0
    for sub in ("harvest-abstracts", "download-fulltext", "download-annotations", "update", "version"):
        assert sub in result.output


def test_version_command() -> None:
    result = CliRunner().invoke(cli, ["version"])
    assert result.exit_code == 0
    assert "europepmc-bulk" in result.output
