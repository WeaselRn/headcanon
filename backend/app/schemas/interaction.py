"""
Pydantic v2 Schemas for Interaction API endpoints.

Reference: docs/api/04_interaction.md
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.engines.interaction_engine import InteractionResult


class InteractionRequest(BaseModel):
    """Request payload to process a user interaction."""

    universe_id: str = Field(min_length=1)
    user_input: str = Field(min_length=1, description="Player action text.")
    user_character_id: str = Field(default="char_user")


class InteractionResponse(BaseModel):
    """Response payload containing InteractionResult."""

    interaction_result: InteractionResult
