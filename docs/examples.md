# Examples

## Harvest a year range in JSON and XML in parallel

```python
from europepmc_bulk import Config, AbstractHarvester

cfg = Config(base_dir="./data")
cfg.ensure_dirs()
AbstractHarvester(cfg).harvest_years(2020, 2024, formats=["json", "xml"], max_workers=5)
```

## Get a single article's full text

```python
from europepmc_bulk import Config, ArticlesClient

c = ArticlesClient(Config())
xml = c.get_full_text_xml("PMC1234567")
```

## Collect annotations for a fixed list of PMIDs

```python
from pathlib import Path
from europepmc_bulk import Config, AnnotationsCollector

cfg = Config(base_dir="./data")
cfg.ensure_dirs()
ids = ["MED:35305722", "MED:18690725"]
AnnotationsCollector(cfg).collect(ids, output_dir=cfg.annotations_dir)
```
