"""
Simulation API Routes.

Executes pending world effects, applies permanent state updates, and persists WorldState.

Reference: docs/api/05_simulation.md
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import (
    get_simulation_engine,
    get_universe_repository,
    get_world_state_repository,
)
from app.engines.simulation_engine import SimulationEngine
from app.repositories.exceptions import UniverseNotFoundError, WorldStateNotFoundError
from app.repositories.universe_repository import UniverseRepository
from app.repositories.world_state_repository import WorldStateRepository
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.schemas.universe import ErrorResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Simulation"])


@router.post(
    "/simulate",
    response_model=SimulationResponse,
    summary="Simulate World Consequences",
    description="Execute pending world effects from an interaction and update WorldState.",
    responses={
        400: {"model": ErrorResponse, "description": "Simulation Failure"},
        404: {"model": ErrorResponse, "description": "Universe or WorldState Not Found"},
    },
)
def run_simulation(
    req: SimulationRequest,
    universe_repo: UniverseRepository = Depends(get_universe_repository),
    world_state_repo: WorldStateRepository = Depends(get_world_state_repository),
    simulation_engine: SimulationEngine = Depends(get_simulation_engine),
) -> SimulationResponse:
    """Execute pending world effects and persist updated WorldState."""
    try:
        universe = universe_repo.load_universe(req.universe_id)
        world_state = world_state_repo.load(req.universe_id)
    except (UniverseNotFoundError, WorldStateNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        result = simulation_engine.simulate_interaction(
            interaction_result=req.interaction_result,
            world_state=world_state,
            universe=universe,
            user_character_id=req.user_character_id,
        )

        if not result.success:
            raise HTTPException(
                status_code=400, detail=result.error_message or "Simulation failed."
            )

        # Persist updated WorldState
        world_state_repo.save(result.updated_world_state)

        return SimulationResponse(
            simulation_result=result,
            world_state=result.updated_world_state,
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        logger.error("World simulation failed: %s", exc)
        raise HTTPException(status_code=400, detail=f"Simulation failed: {exc}") from exc
