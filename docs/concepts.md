# Concepts

## Cursor pagination

Europe PMC's REST search uses an opaque ``cursorMark`` parameter to paginate results
deterministically. europepmc-bulk persists the cursor to disk after every page, so
interruptions resume cleanly.

## Resume state

Every harvester writes a JSON file under ``config.state_dir/<harvester>.json`` keyed
by the year + format being harvested. The file is updated atomically (tempfile +
``os.replace``) on every progress step.

## Atomic writes

All output files are written to a sibling ``.tmp`` then renamed. A crash mid-write
leaves the previous good file intact and no partial files behind.

## Rate limiting

A token-bucket ``RateLimiter`` is shared across all threads in a harvester instance,
so total request rate stays under the configured limit (default 10 req/s) regardless
of worker count.
