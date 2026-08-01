"""
Relationship data models for Headcanon.

Relationships connect entities and are stored independently of characters to
prevent data duplication.  They are **directional** (A → B ≠ B → A) and
**multidimensional** (trust, respect, affection, fear, suspicion, loyalty).

Mutable runtime values (scores, history) live here because relationships
evolve during simulation.  The Universe Builder produces the initial values;
the Simulation Engine updates them.

Reference: docs/universe/6_relationship.md, docs/universe/1_universe_schema §9
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator

from app.world.character import EntityMetadata

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class RelationshipType(StrEnum):
    """Descriptive relationship category between two entities."""

    FRIEND = "Friend"
    ENEMY = "Enemy"
    FAMILY = "Family"
    MENTOR = "Mentor"
    STUDENT = "Student"
    ALLY = "Ally"
    NEUTRAL = "Neutral"
    ROMANTIC = "Romantic"
    RIVAL = "Rival"
    EMPLOYER = "Employer"
    FOLLOWER = "Follower"
    COMPANION = "Companion"
    STRANGER = "Stranger"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class RelationshipScores(BaseModel):
    """
    Multidimensional scores capturing the nuance of a relationship.

    Every score is clamped to [0, 100].  The Simulation Engine is responsible
    for enforcing these bounds when updating values.

    Attributes:
        trust:     Belief in the target's intentions (0 = none, 100 = absolute).
        respect:   Admiration for the target's skill or character.
        affection: Emotional closeness (friendship, love, care).
        fear:      Intimidation / wariness towards the target.
        suspicion: Uncertainty about the target's motives.
        loyalty:   Willingness to act on behalf of the target.
    """

    trust: int = Field(default=50, ge=0, le=100)
    respect: int = Field(default=50, ge=0, le=100)
    affection: int = Field(default=50, ge=0, le=100)
    fear: int = Field(default=0, ge=0, le=100)
    suspicion: int = Field(default=0, ge=0, le=100)
    loyalty: int = Field(default=50, ge=0, le=100)


class RelationshipHistoryEntry(BaseModel, frozen=True):
    """
    A single recorded change to the relationship scores.

    Every significant update should be appended; history is never deleted.

    Attributes:
        event:  Human-readable description of what triggered the change
                (e.g. ``"Saved from troll"``).
        change: Description of the score change (e.g. ``"+30 Trust"``).
    """

    event: str
    change: str


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Relationship(BaseModel):
    """
    A directed relationship from one entity to another.

    Relationships capture how ``source`` perceives ``target``.  Because they
    are directional, a pair of characters typically generates two Relationship
    records (one per direction).

    ID convention: ``rel_<source>_<target>``
    (e.g. ``rel_harry_hermione``).

    Attributes:
        id:           Unique relationship identifier.
        source:       ID of the entity that holds this relationship.
        target:       ID of the entity being perceived.
        type:         Descriptive relationship category.
        scores:       Multidimensional relationship scores.
        history:      Ordered log of significant score changes.
        last_updated: UTC timestamp of the most recent update.
        metadata:     Shared entity metadata.
    """

    id: str = Field(pattern=r"^rel_\S+$")
    source: str
    target: str
    type: RelationshipType = RelationshipType.NEUTRAL
    scores: RelationshipScores = Field(default_factory=RelationshipScores)
    history: list[RelationshipHistoryEntry] = Field(default_factory=list)
    last_updated: datetime | None = None
    metadata: EntityMetadata = Field(default_factory=EntityMetadata)

    @field_validator("source", "target")
    @classmethod
    def entity_id_non_empty(cls, v: str) -> str:
        """Entity IDs must be non-empty strings."""
        if not v.strip():
            raise ValueError("Entity ID must not be empty.")
        return v

    @model_validator(mode="after")
    def source_differs_from_target(self) -> Relationship:
        """Characters may not have a relationship with themselves."""
        if self.source == self.target:
            raise ValueError(
                f"A relationship cannot reference the same entity as both "
                f"source and target ('{self.source}')."
            )
        return self
