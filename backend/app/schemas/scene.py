"""
Pydantic v2 Schemas for Scene API endpoints.

Reference: docs/api/03_scene.md
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.world.scene import Scene


class GetSceneRequest(BaseModel):
    """Request payload to get current Scene for a universe."""

    universe_id: str = Field(min_length=1)
    location_id: str | None = None
    user_character_id: str = "char_user"


class RefreshSceneRequest(BaseModel):
    """Request payload to rebuild/refresh current Scene."""

    universe_id: str = Field(min_length=1)
    location_id: str | None = None
    user_character_id: str = "char_user"


class SceneResponse(BaseModel):
    """Response payload containing the generated Scene model."""

    scene: Scene
