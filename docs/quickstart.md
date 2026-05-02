# Quickstart

```python
from europepmc_bulk import Config, AbstractHarvester

config = Config(base_dir="./epmc-data")
config.ensure_dirs()

h = AbstractHarvester(config)
h.harvest_year(2024, output_format="json")
```

Files appear under `./epmc-data/abstracts/json/2024/page_NNNNNN.json`.

If the harvest is interrupted, simply re-run the command — it resumes from the
last saved cursor position.
