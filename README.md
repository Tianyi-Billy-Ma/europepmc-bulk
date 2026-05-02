# europepmc-bulk

[![PyPI](https://img.shields.io/pypi/v/europepmc-bulk)](https://pypi.org/project/europepmc-bulk/)
[![Python](https://img.shields.io/pypi/pyversions/europepmc-bulk)](https://pypi.org/project/europepmc-bulk/)
[![License](https://img.shields.io/pypi/l/europepmc-bulk)](LICENSE)

Bulk, parallel, resumable harvester for the [Europe PMC](https://europepmc.org/) corpus.

`europepmc-bulk` complements the existing [pyeuropepmc](https://pypi.org/project/pyeuropepmc/) package — pyeuropepmc is great for ad-hoc search and per-article analysis; **europepmc-bulk** is built for harvesting the entire 40M-article corpus with cursor pagination, atomic file writes, resume state, and threaded parallelism.

## Features

- REST search with cursor-mark pagination
- Bulk FTP/HTTPS downloads of full-text archives, text-mined CSVs, ID mappings
- Annotations API batch collection
- OAI-PMH incremental updates
- JATS XML parsing
- Atomic file writes for crash safety
- Persistent resume state (interrupt and resume any harvest)
- Token-bucket rate limiter (default 10 req/s, configurable)
- Threaded parallel harvest with shared rate limiter
- Optional async HTTP client (`pip install "europepmc-bulk[async]"`)
- Click CLI mirror of the Python API

## Install

```bash
pip install europepmc-bulk
# or with async client
pip install "europepmc-bulk[async]"
```

## Quick start

```python
from europepmc_bulk import Config, AbstractHarvester

config = Config(base_dir="./epmc-data")
harvester = AbstractHarvester(config)
harvester.harvest_year(2024, output_format="json")
```

```bash
# CLI equivalent
europepmc-bulk harvest-abstracts --start-year 2024 --end-year 2024 --format json
```

See [docs](https://europepmc-bulk.readthedocs.io) for full usage.

## License

MIT — see [LICENSE](LICENSE).

## Citing Europe PMC

If you use this package to collect data from Europe PMC, please cite:

> The Europe PMC Consortium. Europe PMC: a full-text literature database for the life sciences and platform for innovation. *Nucleic Acids Research*, 2014.
