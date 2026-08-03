"""
UniverseRepository for Headcanon.

Handles atomic persistence, retrieval, deletion, and listing of canonical
Universe models on disk using Pydantic v2 serialization.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from pathlib import Path
from typing import List

from pydantic import ValidationError

from app.repositories.exceptions import (
    InvalidStorageDataError,
    UniverseNotFoundError,
)
from app.world.universe import Universe, UniverseMetadata

logger = logging.getLogger(__name__)


def _atomic_write_json(file_path: Path, data_json: str) -> None:
    """Write string data atomically to file_path using a temporary file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(data_json)
    os.replace(temp_path, file_path)


class UniverseRepository:
    """
    Repository for managing persistent immutable Universe objects.

    Storage path layout:
        {base_dir}/universes/{universe_id}/universe.json
        {base_dir}/universes/{universe_id}/metadata.json

    Args:
        base_dir: Path to storage root directory.
    """

    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir)
        self.universes_dir = self.base_dir / "universes"
        self.universes_dir.mkdir(parents=True, exist_ok=True)

    def _get_universe_dir(self, universe_id: str) -> Path:
        if not universe_id or not universe_id.strip():
            raise ValueError("Universe ID cannot be empty.")
        return self.universes_dir / universe_id

    def _get_universe_file(self, universe_id: str) -> Path:
        return self._get_universe_dir(universe_id) / "universe.json"

    def _get_metadata_file(self, universe_id: str) -> Path:
        return self._get_universe_dir(universe_id) / "metadata.json"

    def save_universe(self, universe: Universe) -> None:
        """
        Validate and atomically save a Universe object and its metadata.

        Args:
            universe: Universe Pydantic model instance to save.

        Raises:
            ValueError, ValidationError if universe model or ID is invalid.
        """
        if not isinstance(universe, Universe):
            raise ValueError(f"Expected Universe instance, got {type(universe)}.")

        universe_id = universe.metadata.id
        if not universe_id or not universe_id.strip():
            raise ValueError("Universe metadata ID cannot be empty.")

        # Validate universe model
        try:
            # Re-confirm validation
            Universe.model_validate(universe.model_dump())
        except (ValidationError, ValueError) as exc:
            raise ValueError(f"Invalid Universe model cannot be saved: {exc}") from exc

        universe_dir = self._get_universe_dir(universe_id)
        universe_dir.mkdir(parents=True, exist_ok=True)

        # Create mandatory subdirectories per storage layout schema
        (universe_dir / "snapshots").mkdir(exist_ok=True)
        (universe_dir / "media").mkdir(exist_ok=True)
        (universe_dir / "provenance").mkdir(exist_ok=True)

        # Serialize Universe using Pydantic v2
        universe_json = universe.model_dump_json(indent=2)
        _atomic_write_json(self._get_universe_file(universe_id), universe_json)

        # Serialize metadata.json
        metadata_json = universe.metadata.model_dump_json(indent=2)
        _atomic_write_json(self._get_metadata_file(universe_id), metadata_json)

        logger.info("Saved Universe '%s' to %s", universe_id, universe_dir)

    def load_universe(self, universe_id: str) -> Universe:
        """
        Load and deserialize a Universe object from disk.

        Args:
            universe_id: Unique universe identifier.

        Returns:
            Validated Universe model instance.

        Raises:
            UniverseNotFoundError: If universe directory/file does not exist.
            InvalidStorageDataError: If stored JSON is corrupt or invalid.
        """
        universe_file = self._get_universe_file(universe_id)
        if not universe_file.exists():
            raise UniverseNotFoundError(f"Universe '{universe_id}' not found in storage.")

        try:
            raw_json = universe_file.read_text(encoding="utf-8")
            return Universe.model_validate_json(raw_json)
        except (ValidationError, ValueError, json.JSONDecodeError) as exc:
            raise InvalidStorageDataError(
                f"Corrupt or invalid Universe data for '{universe_id}': {exc}"
            ) from exc

    def exists(self, universe_id: str) -> bool:
        """Return True if the specified universe exists in storage."""
        if not universe_id or not universe_id.strip():
            return False
        return self._get_universe_file(universe_id).exists()

    def delete(self, universe_id: str) -> None:
        """
        Delete a universe directory and all associated files/snapshots.

        Args:
            universe_id: ID of the universe to delete.

        Raises:
            UniverseNotFoundError: If the universe does not exist.
        """
        universe_dir = self._get_universe_dir(universe_id)
        if not universe_dir.exists():
            raise UniverseNotFoundError(f"Cannot delete universe '{universe_id}': not found.")

        shutil.rmtree(universe_dir)
        logger.info("Deleted Universe '%s' from %s", universe_id, universe_dir)

    def list(self) -> List[str]:
        """
        Return a list of all saved universe IDs.

        Returns:
            Sorted list of universe ID strings.
        """
        if not self.universes_dir.exists():
            return []

        ids: List[str] = []
        for item in self.universes_dir.iterdir():
            if item.is_dir() and (item / "universe.json").exists():
                ids.append(item.name)
        return sorted(ids)

    def list_metadata(self) -> List[UniverseMetadata]:
        """
        Return a list of UniverseMetadata objects for all saved universes.

        Returns:
            List of UniverseMetadata models.
        """
        metadata_list: List[UniverseMetadata] = []
        for uid in self.list():
            meta_file = self._get_metadata_file(uid)
            if meta_file.exists():
                try:
                    meta = UniverseMetadata.model_validate_json(
                        meta_file.read_text(encoding="utf-8")
                    )
                    metadata_list.append(meta)
                except Exception as exc:
                    logger.warning("Failed to parse metadata for universe '%s': %s", uid, exc)
        return metadata_list
