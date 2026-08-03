"""
Pydantic v2 Schemas for Universe API endpoints.

Reference: docs/api/01_import.md, docs/api/02_universe.md
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ImportUniverseRequest(BaseModel):
    """Request payload to import a story and compile a Universe."""

    source_type: str = Field(
        default="text",
        description="Format of story source ('text', 'pdf', 'epub', 'web').",
    )
    text: str | None = Field(default=None, description="Plain text content if source_type='text'.")
    file_path: str | None = Field(
        default=None, description="Local path to file if source_type is file."
    )
    url: str | None = Field(default=None, description="Web URL if source_type='web'.")
    title: str | None = Field(default=None, description="Optional title override.")
    author: str | None = Field(default=None, description="Optional author override.")


class ImportUniverseResponse(BaseModel):
    """Response payload returned upon successful universe construction."""

    universe_id: str = Field(min_length=1)
    status: str = "completed"
    title: str
    author: str = "Unknown"
    characters_count: int = 0
    locations_count: int = 0
    world_state_version: int = 1


class UniverseMetadataResponse(BaseModel):
    """Metadata summary of a Headcanon Universe."""

    universe_id: str
    title: str
    author: str = "Unknown"
    created_at: datetime | None = None
    characters_count: int = 0
    locations_count: int = 0


class UniverseListResponse(BaseModel):
    """List of all available universes."""

    universes: list[UniverseMetadataResponse] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Standard HTTP error payload."""

    error: str
    detail: str | None = None
    status_code: int = 400
