"""
Event data models for Headcanon.

The Event System manages all occurrences within the universe — from canonical
story milestones to simulation-generated incidents and user-driven actions.
Events are the primary mechanism by which the simulation advances.

Events are **never deleted**.  Completed and cancelled events are preserved
permanently in history.

Reference: docs/universe/10_events.md, docs/universe/5_timeline.md
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from app.world.character import EntityMetadata
from app.world.timeline import EventStatus, EventType

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class EventCategory(StrEnum):
    """Source-level category distinguishing how an event was generated."""

    CANON = "Canon"
    SIMULATION = "Simulation"
    USER = "User"
    WORLD = "World"
    CHARACTER = "Character"


class EventPriority(StrEnum):
    """Execution priority for the event queue."""

    CRITICAL = "Critical"
    MAJOR = "Major"
    NORMAL = "Normal"
    MINOR = "Minor"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class EventConsequence(BaseModel, frozen=True):
    """
    A declared consequence of an event.

    The Simulation Engine uses these to propagate world changes after
    an event completes.

    Attributes:
        description: Human-readable description of what changes.
        entity_id:   Optional ID of the affected entity.
        change_type: Short label for the type of change
                     (e.g. ``"RelationshipUpdate"``, ``"InventoryChange"``).
    """

    description: str
    entity_id: str | None = None
    change_type: str | None = None


class EventHistoryRecord(BaseModel, frozen=True):
    """
    A permanent record of a completed or cancelled event, including its
    final outcome and generated consequences.

    Attributes:
        event_id:     ID of the original event.
        final_status: Status at time of archival.
        timestamp:    In-universe timestamp when the event resolved.
        consequences: Consequences that were applied.
    """

    event_id: str
    final_status: EventStatus
    timestamp: str | None = None
    consequences: list[EventConsequence] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Event(BaseModel, frozen=True):
    """
    A single world event recorded in the universe.

    Events reference entity IDs — never names — to maintain referential
    integrity as the world evolves.

    ID convention: ``evt_<name>``  (e.g. ``evt_sorting``, ``evt_troll_attack``).

    Attributes:
        id:            Immutable unique event identifier.
        title:         Human-readable event name.
        description:   Brief narrative summary of what occurred.
        type:          Timeline event type (Story Event, Combat, etc.).
        category:      Source category (Canon, Simulation, User, World, Character).
        priority:      Queue priority for the Simulation Engine.
        timestamp:     Abstract in-universe timestamp (e.g. ``"Day 14, Morning"``).
        participants:  Character IDs involved.
        location:      Location ID where the event occurred.
        trigger:       Human-readable description of what triggered this event.
        prerequisites: Event IDs or condition strings that must be satisfied first.
        consequences:  Declared world changes produced by this event.
        status:        Current lifecycle status.
        importance:    Importance score (0–100).
        causes:        Event IDs that directly caused this event.
        metadata:      Shared entity metadata.
    """

    id: str = Field(pattern=r"^evt_\S+$")
    title: str = Field(min_length=1)
    description: str = ""
    type: EventType = EventType.STORY_EVENT
    category: EventCategory = EventCategory.CANON
    priority: EventPriority = EventPriority.NORMAL
    timestamp: str | None = None
    participants: list[str] = Field(default_factory=list)
    location: str | None = None
    trigger: str | None = None
    prerequisites: list[str] = Field(default_factory=list)
    consequences: list[EventConsequence] = Field(default_factory=list)
    status: EventStatus = EventStatus.SCHEDULED
    importance: int = Field(default=50, ge=0, le=100)
    causes: list[str] = Field(default_factory=list)
    metadata: EntityMetadata = Field(default_factory=EntityMetadata)

    @field_validator("participants")
    @classmethod
    def participants_are_unique(cls, v: list[str]) -> list[str]:
        """Reject duplicate participant IDs."""
        if len(v) != len(set(v)):
            raise ValueError("Event participant IDs must be unique.")
        return v
