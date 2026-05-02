"""Atomic file writes via tempfile + os.replace."""

from __future__ import annotations

import contextlib
import os
import tempfile
from pathlib import Path


def atomic_write(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write ``content`` to ``path`` atomically.

    Writes to a sibling tempfile then renames. On any failure, the original file
    at ``path`` (if any) is preserved and no partial file is left behind.

    Parameters
    ----------
    path
        Destination file path. Parent directories are created if missing.
    content
        Text content to write.
    encoding
        Text encoding (default UTF-8).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding=encoding) as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(FileNotFoundError):
            os.unlink(tmp)
        raise
