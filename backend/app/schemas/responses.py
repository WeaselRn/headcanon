"""
Legacy API Response Schemas.

Retained for backwards compatibility with legacy story endpoints.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = "ok"


class ErrorResponse(BaseModel):
    """Legacy error response model."""

    detail: str = Field(min_length=1)


class StoryResponse(BaseModel):
    """Legacy story response model."""

    story_id: str
    title: str = ""
    universe: str = ""
    character_name: str = ""
    role: str = ""
    mood: str = ""
    story: str = ""
    thumbnail: str = ""
    scenes: list[dict[str, Any]] = Field(default_factory=list)


class RegenerateSceneResponse(BaseModel):
    """Legacy regenerate scene response model."""

    story_id: str
    scene_number: int
    image_url: str = ""
