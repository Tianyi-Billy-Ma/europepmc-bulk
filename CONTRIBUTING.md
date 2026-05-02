# Contributing

## Dev setup

```bash
git clone https://github.com/Tianyi-Billy-Ma/europepmc-bulk
cd europepmc-bulk
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev,async,docs]"
pre-commit install
```

## Run tests

```bash
# Unit tests only (no network)
pytest -m "not live"

# Including live API tests (slow, requires network)
pytest
```

## Lint and typecheck

```bash
ruff check src tests
ruff format src tests
mypy src
```

## Build docs locally

```bash
mkdocs serve
```

## Release process

1. Update `CHANGELOG.md` (move `[Unreleased]` items into a new version section)
2. Bump `src/europepmc_bulk/_version.py`
3. Commit, tag `vX.Y.Z`, push tag
4. GitHub Actions publishes to PyPI on tag push
