"""Tests for ResumeState (persistent JSON KV store)."""

import json
import threading
from pathlib import Path

from europepmc_bulk.persistence.resume_state import ResumeState


def test_get_default_when_missing(tmp_state_file: Path) -> None:
    state = ResumeState(tmp_state_file)
    assert state.get("missing", default="d") == "d"


def test_set_and_get_roundtrip(tmp_state_file: Path) -> None:
    state = ResumeState(tmp_state_file)
    state.set("k", 123)
    assert state.get("k") == 123
    on_disk = json.loads(tmp_state_file.read_text())
    assert on_disk == {"k": 123}


def test_reload_from_existing_file(tmp_state_file: Path) -> None:
    tmp_state_file.write_text(json.dumps({"a": 1, "b": "hello"}))
    state = ResumeState(tmp_state_file)
    assert state.get("a") == 1
    assert state.get("b") == "hello"


def test_remove_clears_key(tmp_state_file: Path) -> None:
    state = ResumeState(tmp_state_file)
    state.set("k", 1)
    state.remove("k")
    assert state.get("k") is None


def test_corrupt_file_falls_back_to_empty(tmp_state_file: Path) -> None:
    tmp_state_file.write_text("not valid json {{{")
    state = ResumeState(tmp_state_file)
    assert state.get("anything") is None
    state.set("k", 1)
    assert json.loads(tmp_state_file.read_text()) == {"k": 1}


def test_thread_safe_concurrent_writes(tmp_state_file: Path) -> None:
    state = ResumeState(tmp_state_file)

    def worker(prefix: str) -> None:
        for i in range(50):
            state.set(f"{prefix}_{i}", i)

    threads = [threading.Thread(target=worker, args=(p,)) for p in ["a", "b", "c"]]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    on_disk = json.loads(tmp_state_file.read_text())
    assert len(on_disk) == 150
