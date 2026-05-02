"""Persistence layer: atomic writes and resume state."""

from europepmc_bulk.persistence.atomic import atomic_write

__all__ = ["atomic_write"]
