"""
Pydantic v2 Schemas for Simulation API endpoints.

Reference: docs/api/05_simulation.md
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.engines.interaction_engine import InteractionResult
from app.engines.simulation_engine import SimulationResult
from app.world.world_state import WorldState


class SimulationRequest(BaseModel):
    """Request payload to apply pending world effects and simulate consequences."""

    universe_id: str = Field(min_length=1)
    interaction_result: InteractionResult
    user_character_id: str = Field(default="char_user")


class SimulationResponse(BaseModel):
    """Response payload containing SimulationResult and updated WorldState."""

    simulation_result: SimulationResult
    world_state: WorldState
