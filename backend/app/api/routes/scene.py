"""
Scene API Routes.

Handles fetching and refreshing UI-ready Scene models.

Reference: docs/api/03_scene.md
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_scene_engine,
    get_universe_repository,
    get_world_state_repository,
)
from app.engines.scene_engine import SceneEngine
from app.repositories.exceptions import UniverseNotFoundError, WorldStateNotFoundError
from app.repositories.universe_repository import UniverseRepository
from app.repositories.world_state_repository import WorldStateRepository
from app.schemas.scene import RefreshSceneRequest, SceneResponse
from app.schemas.universe import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/scene", tags=["Scene"])


@router.get(
    "",
    response_model=SceneResponse,
    summary="Get Current Scene",
    description="Construct and return a UI-ready Scene object for the active location.",
    responses={
        404: {"model": ErrorResponse, "description": "Universe or WorldState Not Found"},
    },
)
def get_scene(
    universe_id: str,
    location_id: str | None = None,
    user_character_id: str = "char_user",
    universe_repo: UniverseRepository = Depends(get_universe_repository),
    world_state_repo: WorldStateRepository = Depends(get_world_state_repository),
    scene_engine: SceneEngine = Depends(get_scene_engine),
) -> SceneResponse:
    """Fetch current Scene for the given universe."""
    try:
        universe = universe_repo.load_universe(universe_id)
        world_state = world_state_repo.load(universe_id)
    except (UniverseNotFoundError, WorldStateNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        scene = scene_engine.build_scene(
            universe=universe,
            world_state=world_state,
            location_id=location_id,
            user_character_id=user_character_id,
        )
        return SceneResponse(scene=scene)
    except Exception as exc:
        logger.error("Failed to construct scene: %s", exc)
        raise HTTPException(status_code=400, detail=f"Scene construction failed: {exc}") from exc


@router.post(
    "/refresh",
    response_model=SceneResponse,
    summary="Refresh Current Scene",
    description="Rebuild and return a refreshed Scene object after world state mutations.",
    responses={
        404: {"model": ErrorResponse, "description": "Universe or WorldState Not Found"},
    },
)
def refresh_scene(
    req: RefreshSceneRequest,
    universe_repo: UniverseRepository = Depends(get_universe_repository),
    world_state_repo: WorldStateRepository = Depends(get_world_state_repository),
    scene_engine: SceneEngine = Depends(get_scene_engine),
) -> SceneResponse:
    """Rebuild and return refreshed Scene object."""
    try:
        universe = universe_repo.load_universe(req.universe_id)
        world_state = world_state_repo.load(req.universe_id)
    except (UniverseNotFoundError, WorldStateNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        scene = scene_engine.build_scene(
            universe=universe,
            world_state=world_state,
            location_id=req.location_id,
            user_character_id=req.user_character_id,
        )
        return SceneResponse(scene=scene)
    except Exception as exc:
        logger.error("Failed to refresh scene: %s", exc)
        raise HTTPException(status_code=400, detail=f"Scene refresh failed: {exc}") from exc
