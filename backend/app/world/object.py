"""
Object data models for Headcanon.

Objects represent every significant physical (or virtual) entity that can be
owned, moved, used, destroyed, or interacted with.  They are **immutable
canonical definitions**; mutable runtime state (current owner, condition,
visibility) lives exclusively in the World State.

Reference: docs/universe/4_objects.md, docs/universe/1_universe_schema §8
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from app.world.character import EntityMetadata

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ObjectCategory(StrEnum):
    """Broad category of the object."""

    WEAPON = "Weapon"
    BOOK = "Book"
    POTION = "Potion"
    TOOL = "Tool"
    KEY = "Key"
    VEHICLE = "Vehicle"
    FOOD = "Food"
    TREASURE = "Treasure"
    ARTIFACT = "Artifact"
    CLOTHING = "Clothing"
    FURNITURE = "Furniture"
    DOCUMENT = "Document"
    CREATURE_ITEM = "Creature Item"
    MAGIC_ITEM = "Magic Item"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class ObjectAppearance(BaseModel, frozen=True):
    """
    Visual metadata used by the Media Pipeline.

    Attributes:
        color:     Dominant colour (e.g. ``"Dark Brown"``).
        material:  Primary material (e.g. ``"Elder Wood"``).
        size:      Size descriptor (e.g. ``"15 inches"``).
        condition: Visual condition (e.g. ``"Pristine"``).
    """

    color: str | None = None
    material: str | None = None
    size: str | None = None
    condition: str | None = None


class ObjectProperties(BaseModel, frozen=True):
    """
    Immutable physical / magical characteristics.

    These fields never change after the Universe Builder assigns them.
    Current condition belongs in the World State.

    Attributes:
        weight:   Qualitative weight descriptor (e.g. ``"1 kg"``).
        rarity:   Rarity tier (e.g. ``"Legendary"``).
        material: Primary material.
        magic:    Whether the object is magical.
    """

    weight: str | None = None
    rarity: str | None = None
    material: str | None = None
    magic: bool = False


class ObjectHistoryEntry(BaseModel, frozen=True):
    """
    A single recorded state-change in the object's provenance.

    Every major transfer or transformation is appended here.
    History entries are never removed.

    Attributes:
        event: Human-readable description of what happened
               (e.g. ``"Transferred to Harry"``).
    """

    event: str


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Object(BaseModel, frozen=True):
    """
    Canonical definition of a world object.

    Objects store *what the item is*, never *where it is right now*.
    Current ownership, location, condition, and visibility belong in the
    World State.

    ID convention: ``obj_<name>``  (e.g. ``obj_elder_wand``, ``obj_sorting_hat``).

    Attributes:
        id:          Immutable unique object identifier.
        name:        Canonical object name.
        aliases:     Alternative names used for entity resolution.
        category:    Broad object category.
        description: Permanent canonical description.
        appearance:  Visual attributes for media generation.
        properties:  Immutable physical / magical characteristics.
        owner:       Initial canonical owner ID (character, location, or ``None``).
        location:    Initial canonical location ID.
        container:   ID of a containing object, if the item is nested.
        state:       Initial mutable state expressed as free-form key/value pairs.
        abilities:   Actions this object enables (e.g. ``["Cast Magic"]``).
        history:     Ordered provenance log of major state changes.
        metadata:    Shared entity metadata.
    """

    id: str = Field(pattern=r"^obj_\S+$")
    name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    category: ObjectCategory | None = None
    description: str = ""
    appearance: ObjectAppearance = Field(default_factory=ObjectAppearance)
    properties: ObjectProperties = Field(default_factory=ObjectProperties)
    owner: str | None = None
    location: str | None = None
    container: str | None = None
    state: dict[str, bool | int | float | str] = Field(default_factory=dict)
    abilities: list[str] = Field(default_factory=list)
    history: list[ObjectHistoryEntry] = Field(default_factory=list)
    metadata: EntityMetadata = Field(default_factory=EntityMetadata)
