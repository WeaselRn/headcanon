"""
Pydantic v2 Schemas for Media API endpoints.

Reference: docs/api/06_media.md
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.engines.media_pipeline import AssetMetadata, MediaPipelineResult
from app.world.scene import Scene


class MediaGenerationRequest(BaseModel):
    """Request payload to generate media for a Scene."""

    universe_id: str = Field(min_length=1)
    scene: Scene


class MediaGenerationResponse(BaseModel):
    """Response payload containing MediaPipelineResult."""

    result: MediaPipelineResult


class AssetMetadataResponse(BaseModel):
    """Response payload containing AssetMetadata."""

    asset_metadata: AssetMetadata
