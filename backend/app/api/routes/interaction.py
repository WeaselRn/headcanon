"""
Interaction API Routes.

Handles user actions and orchestrates InteractionEngine responses.

Reference: docs/api/04_interaction.md
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_interaction_engine,
    get_universe_repository,
    get_world_state_repository,
)
from app.engines.interaction_engine import InteractionEngine
from app.repositories.exceptions import UniverseNotFoundError, WorldStateNotFoundError
from app.repositories.universe_repository import UniverseRepository
from app.repositories.world_state_repository import WorldStateRepository
from app.schemas.interaction import InteractionRequest, InteractionResponse
from app.schemas.universe import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Interaction"])


@router.post(
    "/interact",
    response_model=InteractionResponse,
    summary="Process User Action",
    description="Accept player input, parse intent, and return InteractionResult.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid Action"},
        404: {"model": ErrorResponse, "description": "Universe or WorldState Not Found"},
    },
)
def process_interaction(
    req: InteractionRequest,
    universe_repo: UniverseRepository = Depends(get_universe_repository),
    world_state_repo: WorldStateRepository = Depends(get_world_state_repository),
    interaction_engine: InteractionEngine = Depends(get_interaction_engine),
) -> InteractionResponse:
    """Process user input through InteractionEngine (read-only, produces pending effects)."""
    try:
        universe = universe_repo.load_universe(req.universe_id)
        world_state = world_state_repo.load(req.universe_id)
    except (UniverseNotFoundError, WorldStateNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        result = interaction_engine.process_action(
            user_input=req.user_input,
            world_state=world_state,
            universe=universe,
            user_character_id=req.user_character_id,
        )
        return InteractionResponse(interaction_result=result)
    except Exception as exc:
        logger.error("Interaction processing failed: %s", exc)
        raise HTTPException(
            status_code=400, detail=f"Interaction processing failed: {exc}"
        ) from exc
