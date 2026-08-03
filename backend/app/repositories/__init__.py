"""
Headcanon Repositories package.

Provides repository interfaces for managing persistent Universe, WorldState,
and Snapshot models.
"""

from app.repositories.exceptions import (
    InvalidStorageDataError,
    RepositoryError,
    SnapshotNotFoundError,
    UniverseNotFoundError,
    WorldStateNotFoundError,
)
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.universe_repository import UniverseRepository
from app.repositories.world_state_repository import WorldStateRepository

__all__ = [
    "UniverseRepository",
    "WorldStateRepository",
    "SnapshotRepository",
    "RepositoryError",
    "UniverseNotFoundError",
    "WorldStateNotFoundError",
    "SnapshotNotFoundError",
    "InvalidStorageDataError",
]
