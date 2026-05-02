"""Thread-safe persistent JSON key-value state for resuming interrupted harvests."""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from europepmc_bulk.persistence.atomic import atomic_write


class ResumeState:
    """Persistent JSON-backed key-value store, thread-safe and crash-safe.

    Reads on construction; writes through ``atomic_write`` so a crash mid-write
    leaves the previous good copy intact. A corrupt or empty file is tolerated
    and treated as an empty store.
    """

    def __init__(self, state_file: Path) -> None:
        self.state_file = state_file
        self._data: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._load()

    def _load(self) -> None:
        if self.state_file.exists():
            try:
                text = self.state_file.read_text().strip()
                if text:
                    self._data = json.loads(text)
            except (json.JSONDecodeError, OSError):
                self._data = {}

    def _save_locked(self) -> None:
        atomic_write(self.state_file, json.dumps(self._data, indent=2))

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._data[key] = value
            self._save_locked()

    def has(self, key: str) -> bool:
        with self._lock:
            return key in self._data

    def remove(self, key: str) -> None:
        with self._lock:
            self._data.pop(key, None)
            self._save_locked()
