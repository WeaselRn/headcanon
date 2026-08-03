"""
SnapshotRepository for Headcanon.

Handles creation, loading, restoration, and listing of versioned point-in-time
Snapshots of the live WorldState on disk using Pydantic v2.
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from app.repositories.exceptions import (
    InvalidStorageDataError,
    SnapshotNotFoundError,
)
from app.repositories.world_state_repository import WorldStateRepository
from app.world.snapshot import (
    Snapshot,
    SnapshotMetadata,
    SnapshotSaveType,
    SnapshotVersionMetadata,
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


class SnapshotRepository:
    """
    Repository for creating, saving, restoring, and listing Snapshots.

    Storage path layout:
        {base_dir}/universes/{universe_id}/snapshots/{snapshot_id}.json

    Args:
        base_dir: Path to storage root directory.
        world_state_repo: Optional WorldStateRepository instance for state restoration.
    """

    def __init__(
        self,
        base_dir: Path | str,
        world_state_repo: WorldStateRepository | None = None,
    ) -> None:
        self.base_dir = Path(base_dir)
        self.universes_dir = self.base_dir / "universes"
        self.world_state_repo = world_state_repo or WorldStateRepository(self.base_dir)

    def _get_snapshots_dir(self, universe_id: str) -> Path:
        if not universe_id or not universe_id.strip():
            raise ValueError("Universe ID cannot be empty.")
        p = self.universes_dir / universe_id / "snapshots"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _get_snapshot_file(self, universe_id: str, snapshot_id: str) -> Path:
        return self._get_snapshots_dir(universe_id) / f"{snapshot_id}.json"

    def create_snapshot(
        self,
        universe_id: str,
        world_state: WorldState,
        description: str | None = None,
        save_type: SnapshotSaveType = SnapshotSaveType.AUTOMATIC,
        timeline_ids: list[str] | None = None,
        media_refs: list[str] | None = None,
    ) -> Snapshot:
        """
        Create and persist a new immutable point-in-time Snapshot.

        Args:
            universe_id: Unique universe identifier.
            world_state: Live WorldState model instance to snapshot.
            description: Optional human-readable description or title.
            save_type:   SnapshotSaveType (AUTOMATIC, MANUAL, CHECKPOINT).
            timeline_ids: Optional list of completed event IDs.
            media_refs:  Optional list of generated media URLs/keys.

        Returns:
            Saved Snapshot model instance.
        """
        if not universe_id or not universe_id.strip():
            raise ValueError("Universe ID cannot be empty.")

        if world_state.universe_id != universe_id:
            raise ValueError(
                f"WorldState universe_id '{world_state.universe_id}' does not match "
                f"snapshot universe_id '{universe_id}'."
            )

        existing_count = len(self.list_snapshots(universe_id))
        version_num = existing_count + 1
        snapshot_id = f"snap_{version_num:03d}_{uuid.uuid4().hex[:6]}"

        now = datetime.now(tz=UTC)
        metadata = SnapshotMetadata(
            created_at=now,
            world_state_version=version_num,
            save_type=save_type,
            description=description,
            versions=SnapshotVersionMetadata(schema_version="1.0"),
        )

        snapshot = Snapshot(
            snapshot_id=snapshot_id,
            universe_id=universe_id,
            world_state=world_state,
            timeline_ids=timeline_ids or [],
            media_refs=media_refs or [],
            metadata=metadata,
        )

        # Validate snapshot
        try:
            Snapshot.model_validate(snapshot.model_dump())
        except (ValidationError, ValueError) as exc:
            raise ValueError(f"Invalid Snapshot cannot be created: {exc}") from exc

        target_file = self._get_snapshot_file(universe_id, snapshot_id)
        snap_json = snapshot.model_dump_json(indent=2)
        _atomic_write_json(target_file, snap_json)

        logger.info("Created Snapshot '%s' for universe '%s'", snapshot_id, universe_id)
        return snapshot

    def load_snapshot(self, universe_id: str, snapshot_id: str) -> Snapshot:
        """
        Load and deserialize a Snapshot by snapshot_id.

        Args:
            universe_id: Unique universe identifier.
            snapshot_id: Unique snapshot identifier.

        Returns:
            Validated Snapshot model instance.

        Raises:
            SnapshotNotFoundError: If snapshot_id does not exist.
            InvalidStorageDataError: If snapshot JSON is corrupt.
        """
        target_file = self._get_snapshot_file(universe_id, snapshot_id)
        if not target_file.exists():
            raise SnapshotNotFoundError(
                f"Snapshot '{snapshot_id}' for universe '{universe_id}' not found."
            )

        try:
            raw_json = target_file.read_text(encoding="utf-8")
            return Snapshot.model_validate_json(raw_json)
        except (ValidationError, ValueError, json.JSONDecodeError) as exc:
            raise InvalidStorageDataError(
                f"Corrupt or invalid Snapshot '{snapshot_id}': {exc}"
            ) from exc

    def restore_snapshot(self, universe_id: str, snapshot_id: str) -> WorldState:
        """
        Restore a past snapshot as the active WorldState for the universe.

        Args:
            universe_id: Unique universe identifier.
            snapshot_id: ID of snapshot to restore.

        Returns:
            Restored active WorldState instance.
        """
        snapshot = self.load_snapshot(universe_id, snapshot_id)

        # Save snapshot's world_state as the active world_state.json
        restored_state = self.world_state_repo.update(universe_id, snapshot.world_state)
        logger.info(
            "Restored WorldState from Snapshot '%s' for universe '%s'", snapshot_id, universe_id
        )
        return restored_state

    def list_snapshots(self, universe_id: str) -> list[Snapshot]:
        """
        List all snapshots for a universe, sorted by creation timestamp.

        Args:
            universe_id: Unique universe identifier.

        Returns:
            List of Snapshot objects ordered by created_at.
        """
        snap_dir = self._get_snapshots_dir(universe_id)
        if not snap_dir.exists():
            return []

        snapshots: list[Snapshot] = []
        for file in snap_dir.glob("*.json"):
            if file.name.endswith(".tmp.json"):
                continue
            try:
                raw_json = file.read_text(encoding="utf-8")
                snap = Snapshot.model_validate_json(raw_json)
                snapshots.append(snap)
            except Exception as exc:
                logger.warning("Failed to parse snapshot file '%s': %s", file, exc)

        return sorted(snapshots, key=lambda s: s.metadata.created_at)
