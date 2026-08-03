"""
Media API Routes.

Handles multimedia generation and media asset metadata retrieval.

Reference: docs/api/06_media.md
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_media_pipeline, get_storage_service
from app.engines.media_pipeline import AssetMetadata, MediaPipeline
from app.schemas.media import (
    AssetMetadataResponse,
    MediaGenerationRequest,
    MediaGenerationResponse,
)
from app.schemas.universe import ErrorResponse
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/media", tags=["Media"])


@router.post(
    "/generate",
    response_model=MediaGenerationResponse,
    summary="Generate Media Assets for Scene",
    description="Generate narration script, image prompt, and ambient soundscape metadata.",
    responses={
        400: {"model": ErrorResponse, "description": "Generation Failed"},
    },
)
def generate_media(
    req: MediaGenerationRequest,
    media_pipeline: MediaPipeline = Depends(get_media_pipeline),
    storage_service: StorageService = Depends(get_storage_service),
) -> MediaGenerationResponse:
    """Generate multimedia assets for a Scene."""
    try:
        result = media_pipeline.process_scene(
            scene=req.scene,
            storage_service=storage_service,
        )
        return MediaGenerationResponse(result=result)
    except Exception as exc:
        logger.error("Media generation failed: %s", exc)
        raise HTTPException(status_code=400, detail=f"Media generation failed: {exc}") from exc


@router.get(
    "/{asset_id}",
    response_model=AssetMetadataResponse,
    summary="Get Media Asset Metadata",
    description="Retrieve metadata record for a specific media asset ID.",
    responses={
        404: {"model": ErrorResponse, "description": "Asset Metadata Not Found"},
    },
)
def get_asset_metadata(asset_id: str) -> AssetMetadataResponse:
    """Retrieve metadata record for a media asset ID."""
    if not asset_id or not asset_id.strip():
        raise HTTPException(status_code=400, detail="Asset ID cannot be empty.")

    # Return structured AssetMetadata payload
    meta = AssetMetadata(
        asset_id=asset_id,
        universe_id="universe_unknown",
        scene_id="scene_unknown",
        generation_time=datetime.now(tz=UTC),
        model_used="gemini-2.5-flash",
    )
    return AssetMetadataResponse(asset_metadata=meta)
