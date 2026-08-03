"""
Universe API Routes.

Handles story import, Universe metadata retrieval, listing, and deletion.

Reference: docs/api/01_import.md, docs/api/02_universe.md
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import (
    get_ai_adapter,
    get_universe_repository,
    get_world_state_repository,
)
from app.engines.universe_builder import BuildRequest, UniverseBuilder
from app.importers.epub_importer import EPUBImporter
from app.importers.pdf_importer import PDFImporter
from app.importers.text_importer import TextImporter
from app.importers.web_importer import WebImporter
from app.repositories.exceptions import UniverseNotFoundError
from app.repositories.universe_repository import UniverseRepository
from app.repositories.world_state_repository import WorldStateRepository
from app.schemas.universe import (
    ErrorResponse,
    ImportUniverseRequest,
    ImportUniverseResponse,
    UniverseListResponse,
    UniverseMetadataResponse,
)
from app.world.timeline import WorldTime
from app.world.world_state import CharacterState, LocationState, WorldState

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/universes", tags=["Universe"])


@router.post(
    "/import",
    response_model=ImportUniverseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Import Story and Reconstruct Universe",
    description="Import raw story text, PDF, EPUB, or URL into a validated Universe model.",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid Request"},
        422: {"model": ErrorResponse, "description": "Universe Construction Failed"},
    },
)
def import_universe(
    req: ImportUniverseRequest,
    universe_repo: UniverseRepository = Depends(get_universe_repository),
    world_state_repo: WorldStateRepository = Depends(get_world_state_repository),
    ai_adapter: Any = Depends(get_ai_adapter),
) -> ImportUniverseResponse:
    """Import story content and construct a persistent Universe."""
    logger.info("Import request received for source_type='%s'", req.source_type)

    story_text = ""
    st_type = req.source_type.lower()

    try:
        if st_type == "text":
            if not req.text or not req.text.strip():
                raise HTTPException(
                    status_code=400, detail="Text content is required for source_type='text'."
                )
            doc = TextImporter().import_story(req.text)
            story_text = doc.cleaned_text
        elif st_type == "pdf":
            if not req.file_path:
                raise HTTPException(
                    status_code=400, detail="file_path is required for source_type='pdf'."
                )
            doc = PDFImporter().import_story(req.file_path)
            story_text = doc.cleaned_text
        elif st_type == "epub":
            if not req.file_path:
                raise HTTPException(
                    status_code=400, detail="file_path is required for source_type='epub'."
                )
            doc = EPUBImporter().import_story(req.file_path)
            story_text = doc.cleaned_text
        elif st_type == "web":
            if not req.url:
                raise HTTPException(
                    status_code=400, detail="url is required for source_type='web'."
                )
            doc = WebImporter().import_story(req.url)
            story_text = doc.cleaned_text
        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported source_type '{req.source_type}'."
            )
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise exc
        logger.error("Text extraction failed: %s", exc)
        raise HTTPException(status_code=400, detail=f"Text extraction failed: {exc}") from exc

    # Compile Universe via UniverseBuilder
    builder = UniverseBuilder(ai_client=ai_adapter)
    try:
        build_req = BuildRequest(
            story_text=story_text,
            title=req.title or "Untitled Story",
            author=req.author or "Unknown",
        )
        build_res = builder.build(build_req)
        universe = build_res.universe
    except Exception as exc:
        logger.error("UniverseBuilder compilation failed: %s", exc)
        raise HTTPException(status_code=422, detail=f"Universe construction failed: {exc}") from exc

    # Initialize live WorldState
    char_states = {
        c.id: CharacterState(
            character_id=c.id,
            location=universe.locations[0].id if universe.locations else None,
        )
        for c in universe.characters
    }
    loc_states = {
        loc.id: LocationState(
            location_id=loc.id,
            occupants=[c.id for c in universe.characters if getattr(c, "location", None) == loc.id],
        )
        for loc in universe.locations
    }

    world_state = WorldState(
        universe_id=universe.metadata.id,
        time=WorldTime(day=1, hour=8),
        characters=char_states,
        locations=loc_states,
    )

    # Persist Universe and WorldState
    try:
        universe_repo.save_universe(universe)
        world_state_repo.save(world_state)
    except Exception as exc:
        logger.error("Failed to persist universe or world state: %s", exc)
        raise HTTPException(status_code=500, detail="Storage persistence failed.") from exc

    return ImportUniverseResponse(
        universe_id=universe.metadata.id,
        status="completed",
        title=universe.metadata.title,
        author=universe.metadata.author or "Unknown",
        characters_count=len(universe.characters),
        locations_count=len(universe.locations),
        world_state_version=1,
    )


@router.get(
    "/{universe_id}",
    response_model=UniverseMetadataResponse,
    summary="Get Universe Metadata",
    description="Retrieve metadata summary for a specific Universe ID.",
    responses={404: {"model": ErrorResponse, "description": "Universe Not Found"}},
)
def get_universe(
    universe_id: str,
    universe_repo: UniverseRepository = Depends(get_universe_repository),
) -> UniverseMetadataResponse:
    """Get metadata summary for a Universe."""
    try:
        universe = universe_repo.load_universe(universe_id)
        return UniverseMetadataResponse(
            universe_id=universe.metadata.id,
            title=universe.metadata.title,
            author=universe.metadata.author or "Unknown",
            created_at=universe.metadata.created_at or datetime.now(tz=UTC),
            characters_count=len(universe.characters),
            locations_count=len(universe.locations),
        )
    except UniverseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Universe '{universe_id}' not found.") from exc


@router.get(
    "",
    response_model=UniverseListResponse,
    summary="List Available Universes",
    description="Retrieve a list of metadata for all saved universes.",
)
def list_universes(
    universe_repo: UniverseRepository = Depends(get_universe_repository),
) -> UniverseListResponse:
    """List metadata for all persistent universes."""
    meta_list = universe_repo.list_metadata()
    responses = [
        UniverseMetadataResponse(
            universe_id=m.id,
            title=m.title,
            author=m.author or "Unknown",
            created_at=m.created_at or datetime.now(tz=UTC),
        )
        for m in meta_list
    ]
    return UniverseListResponse(universes=responses)


@router.delete(
    "/{universe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Universe",
    description="Delete a Universe and all associated snapshots and files.",
    responses={404: {"model": ErrorResponse, "description": "Universe Not Found"}},
)
def delete_universe(
    universe_id: str,
    universe_repo: UniverseRepository = Depends(get_universe_repository),
) -> Response:
    """Delete a persistent Universe."""
    try:
        universe_repo.delete(universe_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except UniverseNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Universe '{universe_id}' not found.") from exc
