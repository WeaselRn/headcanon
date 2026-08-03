"""
Storage & Snapshot API Routes.

Handles snapshot creation, restoration, and snapshot history listing.

Reference: docs/api/07_storage.md
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_snapshot_repository,
    get_world_state_repository,
)
from app.repositories.exceptions import SnapshotNotFoundError, WorldStateNotFoundError
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.world_state_repository import WorldStateRepository
from app.schemas.storage import (
    CreateSnapshotRequest,
    ListSnapshotsResponse,
    RestoreSnapshotRequest,
    SnapshotResponse,
)
from app.schemas.universe import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Storage"])


@router.post(
    "/snapshot",
    response_model=SnapshotResponse,
    summary="Create WorldState Snapshot",
    description="Capture and save a point-in-time snapshot of the current WorldState.",
    responses={
        404: {"model": ErrorResponse, "description": "WorldState Not Found"},
    },
)
def create_snapshot(
    req: CreateSnapshotRequest,
    world_state_repo: WorldStateRepository = Depends(get_world_state_repository),
    snapshot_repo: SnapshotRepository = Depends(get_snapshot_repository),
) -> SnapshotResponse:
    """Create a point-in-time snapshot of current WorldState."""
    try:
        world_state = world_state_repo.load(req.universe_id)
    except WorldStateNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        snapshot = snapshot_repo.create_snapshot(
            universe_id=req.universe_id,
            world_state=world_state,
            description=req.description or f"Snapshot at Day {world_state.time.day}",
        )
        return SnapshotResponse(snapshot=snapshot)
    except Exception as exc:
        logger.error("Failed to create snapshot: %s", exc)
        raise HTTPException(status_code=400, detail=f"Snapshot creation failed: {exc}") from exc


@router.post(
    "/restore",
    response_model=SnapshotResponse,
    summary="Restore WorldState Snapshot",
    description="Restore a previous point-in-time WorldState snapshot.",
    responses={
        404: {"model": ErrorResponse, "description": "Snapshot Not Found"},
    },
)
def restore_snapshot(
    req: RestoreSnapshotRequest,
    world_state_repo: WorldStateRepository = Depends(get_world_state_repository),
    snapshot_repo: SnapshotRepository = Depends(get_snapshot_repository),
) -> SnapshotResponse:
    """Restore a previous snapshot to active WorldState."""
    try:
        restored_state = snapshot_repo.restore_snapshot(
            universe_id=req.universe_id,
            snapshot_id=req.snapshot_id,
        )
        # Save restored state as active WorldState
        world_state_repo.save(restored_state)

        snapshot = snapshot_repo.load_snapshot(req.universe_id, req.snapshot_id)
        return SnapshotResponse(snapshot=snapshot)
    except SnapshotNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        logger.error("Failed to restore snapshot: %s", exc)
        raise HTTPException(status_code=400, detail=f"Snapshot restoration failed: {exc}") from exc


@router.get(
    "/snapshots",
    response_model=ListSnapshotsResponse,
    summary="List Universe Snapshots",
    description="Retrieve all saved snapshots for a Universe ID.",
)
def list_snapshots(
    universe_id: str,
    snapshot_repo: SnapshotRepository = Depends(get_snapshot_repository),
) -> ListSnapshotsResponse:
    """List all saved snapshots for a Universe."""
    try:
        snapshots = snapshot_repo.list_snapshots(universe_id)
        return ListSnapshotsResponse(snapshots=snapshots)
    except Exception as exc:
        logger.error("Failed to list snapshots: %s", exc)
        return ListSnapshotsResponse(snapshots=[])
