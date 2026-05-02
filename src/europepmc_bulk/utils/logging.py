"""Logger setup."""

from __future__ import annotations

import logging
from pathlib import Path


def setup_logger(name: str, log_dir: Path | None = None, level: int = logging.INFO) -> logging.Logger:
    """Return a logger with stream handler (and optional file handler).

    Idempotent — repeated calls with the same ``name`` reuse handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        fmt = logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
        stream = logging.StreamHandler()
        stream.setFormatter(fmt)
        logger.addHandler(stream)
        if log_dir is not None:
            log_dir.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(log_dir / f"{name}.log")
            fh.setFormatter(fmt)
            logger.addHandler(fh)
    return logger
