"""
Location data models for Headcanon.

Locations define every explorable place inside a Headcanon universe.  They are
**immutable canonical definitions**; mutable runtime state (occupants, current
weather, active events) lives exclusively in the World State.

Reference: docs/universe/3_locations.md, docs/universe/1_universe_schema §7
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

from app.world.character import EntityMetadata

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class LocationCategory(StrEnum):
    """Broad spatial category of the location."""

    BUILDING = "Building"
    ROOM = "Room"
    FOREST = "Forest"
    VILLAGE = "Village"
    CASTLE = "Castle"
    MOUNTAIN = "Mountain"
    PLANET = "Planet"
    DUNGEON = "Dungeon"
    SPACECRAFT = "Spacecraft"
    STREET = "Street"
    OCEAN = "Ocean"
    KINGDOM = "Kingdom"
    CITY = "City"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class LocationAppearance(BaseModel, frozen=True):
    """
    Visual metadata used by the Media Pipeline for illustration generation.

    Attributes:
        architecture:     Architectural style (e.g. ``"Gothic"``).
        lighting:         Dominant lighting quality (e.g. ``"Warm"``).
        size:             Scale descriptor (e.g. ``"Massive"``).
        dominant_colors:  List of dominant colour names.
    """

    architecture: str | None = None
    lighting: str | None = None
    size: str | None = None
    dominant_colors: list[str] = Field(default_factory=list)


class LocationEnvironment(BaseModel):
    """
    Current environmental state of the location.

    Unlike the static appearance, environment is *mutable* and is updated by
    the Simulation Engine.

    Attributes:
        weather:      Current weather (e.g. ``"Sunny"``, ``"Rain"``).
        temperature:  Qualitative temperature (e.g. ``"Warm"``).
        time_of_day:  Current time of day (e.g. ``"Morning"``).
        noise:        Ambient noise level (e.g. ``"Quiet"``, ``"Loud"``).
    """

    weather: str | None = None
    temperature: str | None = None
    time_of_day: str | None = None
    noise: str | None = None


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Location(BaseModel, frozen=True):
    """
    Canonical definition of a world location.

    Locations store *what the place is*, never *who is currently there*.
    Occupants, environment, and active events belong in the World State.

    ID convention: ``loc_<name>``  (e.g. ``loc_great_hall``, ``loc_library``).

    Attributes:
        id:                 Immutable unique location identifier.
        name:               Canonical location name.
        aliases:            Alternative names used for entity resolution.
        description:        Permanent canonical description of the place.
        category:           Spatial category (Room, Forest, etc.).
        region:             High-level geographic region name.
        parent_location:    ID of the enclosing location, if any.
        connections:        IDs of navigable adjacent locations.
        appearance:         Visual metadata for media generation.
        environment:        Initial environmental state (overridden at runtime).
        occupants:          Canonical initial character IDs present here.
        objects:            Canonical object IDs belonging to this location.
        events:             Canonical event IDs associated with this location.
        rules:              Rule IDs that apply locally within this location.
        metadata:           Shared entity metadata.
    """

    id: str = Field(pattern=r"^loc_\S+$")
    name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    description: str = ""
    category: LocationCategory | None = None
    region: str | None = None
    parent_location: str | None = None
    connections: list[str] = Field(default_factory=list)
    appearance: LocationAppearance = Field(default_factory=LocationAppearance)
    environment: LocationEnvironment = Field(default_factory=LocationEnvironment)
    occupants: list[str] = Field(default_factory=list)
    objects: list[str] = Field(default_factory=list)
    events: list[str] = Field(default_factory=list)
    rules: list[str] = Field(default_factory=list)
    metadata: EntityMetadata = Field(default_factory=EntityMetadata)

    @field_validator("connections")
    @classmethod
    def connections_are_unique(cls, v: list[str]) -> list[str]:
        """Reject duplicate connection entries."""
        if len(v) != len(set(v)):
            raise ValueError("Location connections must be unique.")
        return v

    @field_validator("connections")
    @classmethod
    def connections_are_loc_ids(cls, v: list[str]) -> list[str]:
        """Enforce that all connection IDs follow the ``loc_`` convention."""
        bad = [c for c in v if not c.startswith("loc_")]
        if bad:
            raise ValueError(
                f"All connected location IDs must start with 'loc_'.  Invalid entries: {bad}"
            )
        return v
