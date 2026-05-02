# Command-line interface

```
europepmc-bulk --help
```

## Subcommands

- `harvest-abstracts` — REST search by year range
- `download-fulltext` — bulk download OA archives via FTP
- `download-annotations` — annotations for a PMID/PMCID list
- `update` — OAI-PMH incremental update
- `version` — print version

## Common flags

- `--data-dir PATH` (env: `EUROPEPMC_DATA_DIR`) — base directory for all output
- `--workers INT` — concurrency for parallel jobs

## Example

```bash
europepmc-bulk harvest-abstracts --data-dir ./mydata --start-year 2024 --end-year 2024 --format json
```
