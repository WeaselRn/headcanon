"""
Memory data models for Headcanon.

The Memory System enables characters to retain experiences, form opinions, and
evolve naturally over time.  Rather than storing conversation history, the
system stores **meaningful memories** that influence future decisions,
relationships, emotions, and dialogue.

Every character maintains an independent memory bank.

Reference: docs/universe/13_memory_schema.md
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class MemoryType(StrEnum):
    """Category of experience captured by the memory."""

    CONVERSATION = "Conversation"
    OBSERVATION = "Observation"
    DISCOVERY = "Discovery"
    GIFT = "Gift"
    CONFLICT = "Conflict"
    VICTORY = "Victory"
    DEFEAT = "Defeat"
    TRAVEL = "Travel"
    RELATIONSHIP_CHANGE = "Relationship Change"
    WORLD_EVENT = "World Event"


class MemoryEmotion(StrEnum):
    """Emotional quality associated with a memory."""

    HAPPY = "Happy"
    SAD = "Sad"
    ANGRY = "Angry"
    CURIOUS = "Curious"
    FEARFUL = "Fearful"
    HOPEFUL = "Hopeful"
    PROUD = "Proud"
    GUILTY = "Guilty"
    RELIEVED = "Relieved"
    NEUTRAL = "Neutral"


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Memory(BaseModel, frozen=True):
    """
    A single memory stored by a character.

    Characters never read raw chat logs — they read memories.  High-importance
    memories are prioritised during retrieval and must never be discarded.

    ID convention: ``mem_<id>``  (e.g. ``mem_001``).

    Importance scale:
        *  0–20:  Forgettable
        * 21–60:  Ordinary
        * 61–90:  Important
        * 91–100: Core Memory (never discarded)

    Attributes:
        id:               Unique memory identifier (e.g. ``"mem_001"``).
        character_id:     ID of the character who holds this memory.
        timestamp:        UTC datetime when the memory was created.
        event_id:         Optional ID of the event that produced this memory.
        type:             Category of experience.
        summary:          Concise first-person summary of what was experienced.
        emotional_impact: Emotions associated with this memory (may be multiple).
        importance:       Importance score (0–100).
        participants:     IDs of characters present during the experience.
        location:         Location ID where the experience occurred.
        related_objects:  Object IDs relevant to this memory.
        tags:             Free-form search tags for retrieval.
    """

    id: str = Field(pattern=r"^mem_\S+$")
    character_id: str = Field(min_length=1)
    timestamp: datetime
    event_id: str | None = None
    type: MemoryType = MemoryType.CONVERSATION
    summary: str = Field(min_length=1)
    emotional_impact: list[MemoryEmotion] = Field(default_factory=list)
    importance: int = Field(default=25, ge=0, le=100)
    participants: list[str] = Field(default_factory=list)
    location: str | None = None
    related_objects: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    @field_validator("participants")
    @classmethod
    def participants_are_unique(cls, v: list[str]) -> list[str]:
        """Participant IDs must be unique within a memory record."""
        if len(v) != len(set(v)):
            raise ValueError("Memory participant IDs must be unique.")
        return v

    @field_validator("related_objects")
    @classmethod
    def object_ids_are_unique(cls, v: list[str]) -> list[str]:
        """Object IDs must be unique within a memory record."""
        if len(v) != len(set(v)):
            raise ValueError("Memory related_objects must contain unique IDs.")
        return v
