"""
Legacy Generation API Request Schemas.

Retained for backwards compatibility with legacy story generation endpoints.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class GenerationRequest(BaseModel):
    """Legacy story generation request model."""

    universe: str = Field(min_length=1)
    character_name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    mood: str = Field(min_length=1)
    prompt: str = Field(min_length=1)


class ContinueStoryRequest(BaseModel):
    """Legacy continue story request model."""

    prompt: str = Field(min_length=1)


class RegenerateSceneRequest(BaseModel):
    """Legacy regenerate scene request model."""

    scene_number: int = Field(ge=1)
