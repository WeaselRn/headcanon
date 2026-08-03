"""
WorldStateRepository for Headcanon.

Handles atomic persistence, loading, updating, and version retrieval of mutable
WorldState models on disk using Pydantic v2.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from pydantic import ValidationError

from app.repositories.exceptions import (
    InvalidStorageDataError,
    WorldStateNotFoundError,
)
from app.world.world_state import WorldState

logger = logging.getLogger(__name__)


def _atomic_write_json(file_path: Path, data_json: str) -> None:
    """Write string data atomically to file_path using a temporary file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = file_path.with_suffix(".tmp")
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(data_json)
    os.replace(temp_path, file_path)


class WorldStateRepository:
    """
    Repository for managing mutable WorldState objects.

    Storage path layout:
        {base_dir}/universes/{universe_id}/world_state.json

    Args:
        base_dir: Path to storage root directory.
    """

    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir)
        self.universes_dir = self.base_dir / "universes"

    def _get_world_state_file(self, universe_id: str) -> Path:
        if not universe_id or not universe_id.strip():
            raise ValueError("Universe ID cannot be empty.")
        return self.universes_dir / universe_id / "world_state.json"

    def save(self, world_state: WorldState) -> None:
        """
        Validate and atomically save a WorldState model to disk.

        Args:
            world_state: WorldState instance to save.

        Raises:
            ValueError: If world_state or universe_id is invalid.
        """
        if not isinstance(world_state, WorldState):
            raise ValueError(f"Expected WorldState instance, got {type(world_state)}.")

        universe_id = world_state.universe_id
        if not universe_id or not universe_id.strip():
            raise ValueError("WorldState universe_id cannot be empty.")

        try:
            # Validate model
            WorldState.model_validate(world_state.model_dump())
        except (ValidationError, ValueError) as exc:
            raise ValueError(f"Invalid WorldState model cannot be saved: {exc}") from exc

        target_file = self._get_world_state_file(universe_id)
        ws_json = world_state.model_dump_json(indent=2)
        _atomic_write_json(target_file, ws_json)

        logger.info("Saved WorldState for universe '%s' to %s", universe_id, target_file)

    def load(self, universe_id: str) -> WorldState:
        """
        Load and deserialize the WorldState for the given universe_id.

        Args:
            universe_id: Unique universe identifier.

        Returns:
            Validated WorldState instance.

        Raises:
            WorldStateNotFoundError: If world_state.json is missing.
            InvalidStorageDataError: If stored JSON is corrupt or invalid.
        """
        target_file = self._get_world_state_file(universe_id)
        if not target_file.exists():
            raise WorldStateNotFoundError(
                f"WorldState for universe '{universe_id}' not found in storage."
            )

        try:
            raw_json = target_file.read_text(encoding="utf-8")
            return WorldState.model_validate_json(raw_json)
        except (ValidationError, ValueError, json.JSONDecodeError) as exc:
            raise InvalidStorageDataError(
                f"Corrupt or invalid WorldState data for '{universe_id}': {exc}"
            ) from exc

    def update(self, universe_id: str, world_state: WorldState) -> WorldState:
        """
        Update the WorldState for a universe and return the updated state.

        Args:
            universe_id: Unique universe identifier.
            world_state: New WorldState model instance.

        Returns:
            Saved WorldState instance.
        """
        if world_state.universe_id != universe_id:
            raise ValueError(
                f"WorldState universe_id '{world_state.universe_id}' does not match "
                f"requested universe_id '{universe_id}'."
            )

        self.save(world_state)
        return world_state

    def latest(self, universe_id: str) -> WorldState:
        """
        Return the latest WorldState for the specified universe_id.

        Args:
            universe_id: Unique universe identifier.

        Returns:
            Latest WorldState model instance.
        """
        return self.load(universe_id)
