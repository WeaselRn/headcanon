"""
Snapshot data models for Headcanon.

A Snapshot represents the **complete mutable state** of a universe at a
specific point in time.  It enables users to pause, resume, and roll back
their interactive universe without losing progress.

The immutable Universe Model is never duplicated; snapshots store only the
dynamic World State and associated version metadata.

Reference: docs/universe/15_snapshot_schema.md
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.world.world_state import WorldState

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class SnapshotSaveType(StrEnum):
    """Origin of the snapshot."""

    AUTOMATIC = "Automatic"
    MANUAL = "Manual"
    CHECKPOINT = "Checkpoint"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class SnapshotVersionMetadata(BaseModel, frozen=True):
    """
    Version information stored with every snapshot.

    Used to detect compatibility issues and trigger migrations before
    loading a snapshot created by an older engine version.

    Attributes:
        schema_version: Universe Schema version (e.g. ``"1.0"``).
        engine_version: Headcanon engine version string.
        prompt_version: Prompt template version string.
    """

    schema_version: str = Field(default="1.0", min_length=1)
    engine_version: str | None = None
    prompt_version: str | None = None


class SnapshotMetadata(BaseModel, frozen=True):
    """
    Metadata block attached to every snapshot for auditing and migration.

    Attributes:
        created_at:          UTC datetime when the snapshot was created.
        world_state_version: Monotonically increasing version counter.
        save_type:           How the snapshot was triggered.
        description:         Optional human-readable label.
        versions:            Version identifiers for compatibility checks.
    """

    created_at: datetime
    world_state_version: int = Field(default=1, ge=1)
    save_type: SnapshotSaveType = SnapshotSaveType.AUTOMATIC
    description: str | None = None
    versions: SnapshotVersionMetadata = Field(default_factory=SnapshotVersionMetadata)


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Snapshot(BaseModel, frozen=True):
    """
    A versioned, immutable point-in-time save of the live World State.

    Snapshots are created automatically (after interactions / events) and
    manually (by the user).  Once created, a snapshot must never be mutated.

    Attributes:
        snapshot_id:   Unique snapshot identifier.
        universe_id:   ID of the universe this snapshot belongs to.
        world_state:   Complete mutable World State at the time of snapshotting.
        timeline_ids:  IDs of completed / cancelled / generated events captured.
        media_refs:    URLs or keys of generated media stored separately in B2.
        metadata:      Version and auditing metadata.
    """

    snapshot_id: str = Field(min_length=1)
    universe_id: str = Field(min_length=1)
    world_state: WorldState
    timeline_ids: list[str] = Field(default_factory=list)
    media_refs: list[str] = Field(default_factory=list)
    metadata: SnapshotMetadata
