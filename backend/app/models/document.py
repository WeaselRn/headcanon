"""
Story Document data model for Headcanon story import pipeline.

Represents a normalized story imported from an external source (PDF, EPUB,
TXT, Web) before it is passed to the Universe Builder for reconstruction.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class StoryDocument(BaseModel):
    """
    Common representation of an imported story document.

    Attributes:
        source_type:   Format/source of the imported document
                       (e.g., 'pdf', 'epub', 'txt', 'web', 'ao3', 'wattpad', 'gutenberg').
        title:         Title of the story document.
        author:        Author of the story (defaults to "Unknown" if not found).
        language:      Language of the story document (defaults to "English").
        chapter_count: Number of chapters detected (None if unsegmented).
        raw_text:      Original, uncleaned text extracted from the source.
        cleaned_text:  Normalized, cleaned text ready for the Universe Builder.
        metadata:      Additional metadata key-value pairs (page count, source URL, etc.).
    """

    source_type: str = Field(min_length=1)
    title: str = Field(min_length=1)
    author: str | None = "Unknown"
    language: str | None = "English"
    chapter_count: int | None = None
    raw_text: str = Field(default="")
    cleaned_text: str = Field(default="")
    metadata: dict[str, Any] = Field(default_factory=dict)
