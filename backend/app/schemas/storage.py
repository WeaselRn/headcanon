"""
Pydantic v2 Schemas for Storage and Snapshot API endpoints.

Reference: docs/api/07_storage.md
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.world.snapshot import Snapshot


class CreateSnapshotRequest(BaseModel):
    """Request payload to create a WorldState snapshot."""

    universe_id: str = Field(min_length=1)
    description: str = Field(default="")


class RestoreSnapshotRequest(BaseModel):
    """Request payload to restore a WorldState snapshot."""

    universe_id: str = Field(min_length=1)
    snapshot_id: str = Field(min_length=1)


class SnapshotResponse(BaseModel):
    """Response payload containing Snapshot details."""

    snapshot: Snapshot


class ListSnapshotsResponse(BaseModel):
    """Response payload containing list of snapshots."""

    snapshots: list[Snapshot] = Field(default_factory=list)
