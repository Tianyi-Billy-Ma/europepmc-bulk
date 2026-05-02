# europepmc-bulk

Bulk, parallel, resumable harvester for the Europe PMC corpus.

## What it does

- Harvest the entire Europe PMC abstract corpus by year, with cursor pagination
- Download bulk full-text and text-mined CSV archives via FTP/HTTPS
- Collect semantic annotations in batches
- Run OAI-PMH incremental updates
- Parse JATS XML into a clean dict
- Resume any interrupted harvest from disk state

## Why not pyeuropepmc?

[pyeuropepmc](https://pypi.org/project/pyeuropepmc/) is great for ad-hoc search and
per-article analysis. **europepmc-bulk** is built for *full corpus harvest at scale*:
crash-safe atomic writes, persistent resume state, threaded parallelism, and a focus on
multi-day jobs that survive disk failures and connection drops.
