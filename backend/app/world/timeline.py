"""
Timeline data models for Headcanon.

The Timeline records the chronological evolution of the universe.  It begins
with canonical events extracted by the Universe Builder and evolves as users
interact with the world.

Key design points:
* Events are **never deleted** — cancelled events are marked ``Cancelled``.
* The canonical ``sequence`` field orders events chronologically.
* Branches allow alternate histories without overwriting canon.

Reference: docs/universe/5_timeline.md, docs/universe/1_universe_schema §10
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator

from app.world.character import EntityMetadata

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class EventType(StrEnum):
    """Broad category of a timeline event."""

    STORY_EVENT = "Story Event"
    CONVERSATION = "Conversation"
    COMBAT = "Combat"
    TRAVEL = "Travel"
    DISCOVERY = "Discovery"
    RELATIONSHIP_CHANGE = "Relationship Change"
    ITEM_TRANSFER = "Item Transfer"
    DEATH = "Death"
    QUEST = "Quest"
    ENVIRONMENTAL = "Environmental"
    WORLD_EVENT = "World Event"
    USER_ACTION = "User Action"
    SIMULATION = "Simulation"


class EventStatus(StrEnum):
    """Lifecycle status of a timeline event."""

    SCHEDULED = "Scheduled"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    FAILED = "Failed"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class WorldTime(BaseModel):
    """
    Abstract in-universe time representation.

    Uses abstract day/hour notation that works for every fictional universe
    rather than calendar dates.

    Attributes:
        day:               Ordinal day within the story (1-indexed).
        hour:              Hour of the day (0–23).
        minute:            Minute within the hour (0–59).
        season:            Current season name (e.g. ``"Autumn"``).
        weather:           Global weather description.
        timeline_position: ID of the last completed timeline event.
    """

    day: int = Field(default=1, ge=1)
    hour: int = Field(default=0, ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    season: str | None = None
    weather: str | None = None
    timeline_position: str | None = None


class TimelineBranch(BaseModel, frozen=True):
    """
    An alternate timeline branch created by a user divergence from canon.

    Attributes:
        branch_id:      Unique identifier for this branch.
        origin_event:   Event ID at which the branch diverged.
        description:    Human-readable description of the divergence.
        events:         Ordered list of event IDs that belong to this branch.
    """

    branch_id: str
    origin_event: str
    description: str = ""
    events: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Event (timeline entry)
# ---------------------------------------------------------------------------


class TimelineEvent(BaseModel, frozen=True):
    """
    A single canonical or simulated event in the timeline.

    ID convention: ``evt_<name>``  (e.g. ``evt_sorting``, ``evt_troll_attack``).

    Attributes:
        id:           Immutable unique event identifier.
        title:        Human-readable event name.
        description:  Brief summary of what occurred.
        type:         Broad event category.
        timestamp:    Abstract in-universe timestamp as a human-readable string
                      (e.g. ``"Day 14, Morning"``).
        participants: Character IDs involved in the event.
        location:     Location ID where the event occurred.
        sequence:     Canonical chronological order (unique, monotonically increasing).
        status:       Lifecycle status.
        importance:   Importance score (0 = minor, 100 = critical).
        causes:       Event IDs that directly caused this event.
        consequences: Event IDs that this event directly produced.
        metadata:     Shared entity metadata.
    """

    id: str = Field(pattern=r"^evt_\S+$")
    title: str = Field(min_length=1)
    description: str = ""
    type: EventType = EventType.STORY_EVENT
    timestamp: str | None = None
    participants: list[str] = Field(default_factory=list)
    location: str | None = None
    sequence: int = Field(ge=0)
    status: EventStatus = EventStatus.SCHEDULED
    importance: int = Field(default=50, ge=0, le=100)
    causes: list[str] = Field(default_factory=list)
    consequences: list[str] = Field(default_factory=list)
    metadata: EntityMetadata = Field(default_factory=EntityMetadata)

    @field_validator("participants")
    @classmethod
    def participants_are_unique(cls, v: list[str]) -> list[str]:
        """Reject duplicate participant entries."""
        if len(v) != len(set(v)):
            raise ValueError("Event participant IDs must be unique.")
        return v


# ---------------------------------------------------------------------------
# Timeline container
# ---------------------------------------------------------------------------


class Timeline(BaseModel):
    """
    Container for all timeline events within a universe.

    Provides helpers to query events by status.  The Timeline Engine is
    responsible for maintaining chronological ordering and producing new
    events.

    Attributes:
        current_time:       Current in-universe time.
        events:             All events (canonical + simulated) in any status.
        active_events:      Subset of events with status ``Active``.
        scheduled_events:   Subset of events with status ``Scheduled``.
        completed_events:   Subset of events with status ``Completed``.
        cancelled_events:   Subset of events with status ``Cancelled``.
        branches:           Alternate timeline branches.
        metadata:           Shared entity metadata.
    """

    current_time: WorldTime = Field(default_factory=WorldTime)
    events: list[TimelineEvent] = Field(default_factory=list)
    active_events: list[str] = Field(default_factory=list)
    scheduled_events: list[str] = Field(default_factory=list)
    completed_events: list[str] = Field(default_factory=list)
    cancelled_events: list[str] = Field(default_factory=list)
    branches: list[TimelineBranch] = Field(default_factory=list)
    metadata: EntityMetadata = Field(default_factory=EntityMetadata)

    @model_validator(mode="after")
    def sequence_numbers_are_unique(self) -> Timeline:
        """Sequence numbers must be unique across all events."""
        sequences = [e.sequence for e in self.events]
        if len(sequences) != len(set(sequences)):
            raise ValueError("Timeline event sequence numbers must be unique.")
        return self

    @model_validator(mode="after")
    def events_are_chronologically_ordered(self) -> Timeline:
        """Events list should be ordered by ascending sequence number."""
        sequences = [e.sequence for e in self.events]
        if sequences != sorted(sequences):
            raise ValueError("Timeline events must be ordered by ascending sequence number.")
        return self
