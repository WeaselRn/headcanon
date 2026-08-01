"""
World State data models for Headcanon.

The World State is the **live, mutable** simulation state of a universe.
While the Universe Model stores the canonical structure extracted from the
source story, the World State stores everything that changes as users interact.

Key design contract:
* The Universe is immutable.
* The World State is mutable.
* Every change to the world must go through the World State — never the
  Universe.

Reference: docs/universe/09_world_state.md
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.world.emotion import EmotionCategory
from app.world.timeline import WorldTime

# ---------------------------------------------------------------------------
# Character State
# ---------------------------------------------------------------------------


class CharacterState(BaseModel):
    """
    Mutable runtime state for a single character.

    Does NOT duplicate the canonical Character definition.  Only the values
    that can change during simulation are stored here.

    Attributes:
        character_id:    ID of the canonical Character being tracked.
        location:        Current location ID.
        emotion:         Current primary emotion.
        health:          Qualitative health status (e.g. ``"Healthy"``).
        inventory:       List of object IDs currently held.
        current_goal:    Description of the character's active goal.
        active_memories: IDs of memories currently influencing behaviour.
        current_action:  Short description of what the character is doing now.
    """

    character_id: str = Field(min_length=1)
    location: str | None = None
    emotion: EmotionCategory = EmotionCategory.CALM
    health: str = "Healthy"
    inventory: list[str] = Field(default_factory=list)
    current_goal: str | None = None
    active_memories: list[str] = Field(default_factory=list)
    current_action: str | None = None


# ---------------------------------------------------------------------------
# Location State
# ---------------------------------------------------------------------------


class LocationState(BaseModel):
    """
    Mutable runtime state for a single location.

    Attributes:
        location_id: ID of the canonical Location.
        occupants:   Character IDs currently present.
        objects:     Object IDs currently present.
        status:      Accessibility status (e.g. ``"Open"``, ``"Locked"``).
    """

    location_id: str = Field(min_length=1)
    occupants: list[str] = Field(default_factory=list)
    objects: list[str] = Field(default_factory=list)
    status: str = "Open"


# ---------------------------------------------------------------------------
# Object State
# ---------------------------------------------------------------------------


class ObjectState(BaseModel):
    """
    Mutable runtime state for a single object.

    Attributes:
        object_id:        ID of the canonical Object.
        owner:            Current owner ID (character or location).
        location:         Current location ID.
        condition:        Current physical condition.
        hidden:           Whether the object is currently concealed.
    """

    object_id: str = Field(min_length=1)
    owner: str | None = None
    location: str | None = None
    condition: str = "Good"
    hidden: bool = False


# ---------------------------------------------------------------------------
# Relationship State
# ---------------------------------------------------------------------------


class RelationshipState(BaseModel):
    """
    Mutable runtime relationship scores between two entities.

    Mirrors the core scores from the canonical Relationship model but is
    stored separately in the World State so scores can evolve without
    mutating the immutable Universe.

    Attributes:
        relationship_id: ID of the canonical Relationship.
        trust:           Current trust score (0–100).
        respect:         Current respect score (0–100).
        affection:       Current affection score (0–100).
        fear:            Current fear score (0–100).
        suspicion:       Current suspicion score (0–100).
        loyalty:         Current loyalty score (0–100).
    """

    relationship_id: str = Field(min_length=1)
    trust: int = Field(default=50, ge=0, le=100)
    respect: int = Field(default=50, ge=0, le=100)
    affection: int = Field(default=50, ge=0, le=100)
    fear: int = Field(default=0, ge=0, le=100)
    suspicion: int = Field(default=0, ge=0, le=100)
    loyalty: int = Field(default=50, ge=0, le=100)


# ---------------------------------------------------------------------------
# Active / Pending Event State
# ---------------------------------------------------------------------------


class ActiveEventState(BaseModel):
    """
    Lightweight runtime record for an event currently in progress.

    Attributes:
        id:           Event ID.
        status:       Current lifecycle status.
        participants: Character IDs currently involved.
    """

    id: str = Field(min_length=1)
    status: str = "active"
    participants: list[str] = Field(default_factory=list)


class PendingEventState(BaseModel, frozen=True):
    """
    A future event waiting for activation.

    Attributes:
        id:            Event ID.
        scheduled_for: Abstract in-universe time descriptor (e.g. ``"Day 5, 18:00"``).
    """

    id: str = Field(min_length=1)
    scheduled_for: str | None = None


# ---------------------------------------------------------------------------
# Environmental State
# ---------------------------------------------------------------------------


class EnvironmentState(BaseModel):
    """
    Global environmental state of the universe.

    Attributes:
        weather:     Current weather (e.g. ``"Rain"``).
        temperature: Approximate temperature in degrees Celsius (integer).
        lighting:    Ambient lighting quality (e.g. ``"Dim"``).
        noise:       Ambient noise level (e.g. ``"Quiet"``).
    """

    weather: str | None = None
    temperature: int | None = None
    lighting: str | None = None
    noise: str | None = None


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class WorldState(BaseModel):
    """
    The live simulation state of a universe.

    The Universe defines *what exists*; the World State defines *what is
    happening right now*.

    All lookups are keyed by entity ID (``dict[str, ...]``) rather than arrays
    to achieve O(1) access.

    Attributes:
        universe_id:    ID of the parent universe this state belongs to.
        time:           Current in-universe time.
        scene_id:       ID of the active scene being presented to the user.
        characters:     Character states keyed by character ID.
        locations:      Location states keyed by location ID.
        objects:        Object states keyed by object ID.
        relationships:  Relationship states keyed by relationship ID.
        active_events:  Events currently in progress.
        pending_events: Events scheduled for the future.
        environment:    Global environmental state.
        flags:          Universe-wide boolean / enum flags (e.g. quests, doors).
    """

    universe_id: str = Field(min_length=1)
    time: WorldTime = Field(default_factory=WorldTime)
    scene_id: str | None = None
    characters: dict[str, CharacterState] = Field(default_factory=dict)
    locations: dict[str, LocationState] = Field(default_factory=dict)
    objects: dict[str, ObjectState] = Field(default_factory=dict)
    relationships: dict[str, RelationshipState] = Field(default_factory=dict)
    active_events: list[ActiveEventState] = Field(default_factory=list)
    pending_events: list[PendingEventState] = Field(default_factory=list)
    environment: EnvironmentState = Field(default_factory=EnvironmentState)
    flags: dict[str, bool | str | int] = Field(default_factory=dict)
