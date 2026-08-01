"""
Universe data models for Headcanon.

The Universe is the **single source of truth** for every Headcanon engine.
Every imported story is transformed into exactly one Universe object.

Design principles (from docs/universe/1_universe_schema):
* **Immutable canon** — the Universe is set once by the Universe Builder and
  never modified by user interaction.
* **ID-based references** — every entity is referenced by ID, never by name.
* **No duplication** — each piece of canonical information exists exactly once.
* **Fully serializable** — the Universe is stored as JSON with no circular
  references.

Reference: docs/universe/1_universe_schema
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator

from app.world.character import Character
from app.world.knowledge_graph import KnowledgeGraph
from app.world.location import Location
from app.world.object import Object
from app.world.relationship import Relationship
from app.world.timeline import Timeline, TimelineEvent
from app.world.world_state import WorldState

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class ImportSource(StrEnum):
    """Supported import source formats."""

    PDF = "PDF"
    EPUB = "EPUB"
    TXT = "TXT"
    MARKDOWN = "Markdown"
    AO3 = "AO3"
    WATTPAD = "Wattpad"
    PROJECT_GUTENBERG = "Project Gutenberg"
    CUSTOM = "Custom"


class WorldRuleCategory(StrEnum):
    """Category of a World Rule."""

    PHYSICS = "Physics"
    MAGIC = "Magic"
    TECHNOLOGY = "Technology"
    COMBAT = "Combat"
    MOVEMENT = "Movement"
    SOCIAL = "Social"
    BIOLOGY = "Biology"
    POLITICS = "Politics"
    RELIGION = "Religion"
    ECONOMY = "Economy"
    ENVIRONMENT = "Environment"
    LORE = "Lore"
    TIMELINE = "Timeline"
    INVENTORY = "Inventory"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class UniverseMetadata(BaseModel, frozen=True):
    """
    Identifies and describes the imported universe.

    Attributes:
        id:             Unique universe identifier (e.g. ``"hp_001"``).
                        Must never change after creation.
        title:          Original story title.
        author:         Story author; ``"Unknown"`` if unattributed.
        source:         Import source format.
        language:       Language of the original story (e.g. ``"English"``).
        genre:          List of genre labels (e.g. ``["Fantasy", "Adventure"]``).
        created_at:     UTC timestamp when the universe was created.
        schema_version: Universe Schema version (e.g. ``"1.0"``).
    """

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    author: str = "Unknown"
    source: ImportSource = ImportSource.CUSTOM
    language: str = "English"
    genre: list[str] = Field(default_factory=list)
    created_at: datetime
    schema_version: str = Field(default="1.0", min_length=1)


class WorldRuleCondition(BaseModel, frozen=True):
    """
    A conditional trigger for a World Rule.

    Attributes:
        condition: Human-readable condition string (e.g. ``"Full Moon"``).
        effect:    Effect that applies when the condition is met (e.g. ``"Transform"``).
    """

    condition: str
    effect: str


class WorldRule(BaseModel, frozen=True):
    """
    An immutable law governing what is possible within this universe.

    World Rules originate from the source material.  They constrain every
    engine.  Only the Universe Builder may create or remove rules.

    ID convention: ``rule_<name>``  (e.g. ``rule_magic_requires_wand``).

    Attributes:
        id:          Unique rule identifier.
        name:        Human-readable rule name.
        category:    Rule category.
        description: Clear explanation of the rule.
        priority:    Resolution priority (higher wins on conflict).
        conditions:  Conditional triggers (e.g. werewolf transforms only on full moon).
        effects:     Declared effects when the rule applies.
        exceptions:  Entities or circumstances exempt from the rule.
        immutable:   Always ``True`` for canonical rules.
        metadata:    Optional additional attributes.
    """

    id: str = Field(pattern=r"^rule_\S+$")
    name: str = Field(min_length=1)
    category: WorldRuleCategory
    description: str = Field(min_length=1)
    priority: int = Field(default=50, ge=0, le=100)
    conditions: list[WorldRuleCondition] = Field(default_factory=list)
    effects: list[str] = Field(default_factory=list)
    exceptions: list[str] = Field(default_factory=list)
    immutable: bool = True


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Universe(BaseModel, frozen=True):
    """
    The canonical, immutable representation of a fictional universe.

    One Universe corresponds to exactly one imported story.  All engines
    consume this single object.  After the Universe Builder produces and
    validates a Universe, no engine may modify it; all runtime changes
    belong in the World State.

    Attributes:
        metadata:       Universe identification and provenance.
        characters:     All canonical character definitions.
        locations:      All canonical location definitions.
        objects:        All canonical object definitions.
        relationships:  All canonical character relationships.
        timeline:       Chronological event container with initial events.
        world_rules:    Immutable laws governing the universe.
        knowledge_graph: Semantic entity graph.
        world_state:    Initial World State produced by the Universe Builder.
    """

    metadata: UniverseMetadata
    characters: list[Character] = Field(default_factory=list)
    locations: list[Location] = Field(default_factory=list)
    objects: list[Object] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    timeline: Timeline = Field(default_factory=Timeline)
    world_rules: list[WorldRule] = Field(default_factory=list)
    knowledge_graph: KnowledgeGraph = Field(default_factory=KnowledgeGraph)
    world_state: WorldState | None = None

    # ------------------------------------------------------------------
    # Uniqueness validators
    # ------------------------------------------------------------------

    @field_validator("characters")
    @classmethod
    def character_ids_unique(cls, v: list[Character]) -> list[Character]:
        """All character IDs must be unique within the universe."""
        ids = [c.id for c in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Character IDs must be unique within a universe.")
        return v

    @field_validator("locations")
    @classmethod
    def location_ids_unique(cls, v: list[Location]) -> list[Location]:
        """All location IDs must be unique within the universe."""
        ids = [loc.id for loc in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Location IDs must be unique within a universe.")
        return v

    @field_validator("objects")
    @classmethod
    def object_ids_unique(cls, v: list[Object]) -> list[Object]:
        """All object IDs must be unique within the universe."""
        ids = [o.id for o in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Object IDs must be unique within a universe.")
        return v

    @field_validator("relationships")
    @classmethod
    def relationship_ids_unique(cls, v: list[Relationship]) -> list[Relationship]:
        """All relationship IDs must be unique within the universe."""
        ids = [r.id for r in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Relationship IDs must be unique within a universe.")
        return v

    @field_validator("world_rules")
    @classmethod
    def world_rule_ids_unique(cls, v: list[WorldRule]) -> list[WorldRule]:
        """All world rule IDs must be unique within the universe."""
        ids = [r.id for r in v]
        if len(ids) != len(set(ids)):
            raise ValueError("World Rule IDs must be unique within a universe.")
        return v

    # ------------------------------------------------------------------
    # Cross-reference validators
    # ------------------------------------------------------------------

    @model_validator(mode="after")
    def timeline_participants_exist(self) -> Universe:
        """
        Every participant ID referenced by timeline events must correspond to a
        known character.
        """
        char_ids = {c.id for c in self.characters}
        for event in self.timeline.events:
            unknown = [p for p in event.participants if p not in char_ids]
            if unknown:
                raise ValueError(
                    f"Timeline event '{event.id}' references unknown participant IDs: {unknown}"
                )
        return self

    @model_validator(mode="after")
    def timeline_locations_exist(self) -> Universe:
        """
        Every location referenced by timeline events must correspond to a
        known location.
        """
        loc_ids = {loc.id for loc in self.locations}
        for event in self.timeline.events:
            if event.location is not None and event.location not in loc_ids:
                raise ValueError(
                    f"Timeline event '{event.id}' references unknown location '{event.location}'."
                )
        return self

    @model_validator(mode="after")
    def relationship_entities_exist(self) -> Universe:
        """
        Every source / target referenced by relationships must correspond to a
        known character.
        """
        char_ids = {c.id for c in self.characters}
        for rel in self.relationships:
            if rel.source not in char_ids:
                raise ValueError(f"Relationship '{rel.id}' has unknown source '{rel.source}'.")
            if rel.target not in char_ids:
                raise ValueError(f"Relationship '{rel.id}' has unknown target '{rel.target}'.")
        return self

    @model_validator(mode="after")
    def location_connections_exist(self) -> Universe:
        """
        Every connected location ID must correspond to a known location.
        Locations must not reference themselves.
        """
        loc_ids = {lc.id for lc in self.locations}
        for loc in self.locations:
            if loc.id in loc.connections:
                raise ValueError(f"Location '{loc.id}' has a self-referencing connection.")
            unknown = [c for c in loc.connections if c not in loc_ids]
            if unknown:
                raise ValueError(
                    f"Location '{loc.id}' references unknown connected location IDs: {unknown}"
                )
        return self

    @model_validator(mode="after")
    def timeline_events_have_unique_sequences(self) -> Universe:
        """Delegate to the Timeline model's own validator (belt-and-suspenders)."""
        # Timeline already validates this internally; this ensures it is
        # re-confirmed at the Universe level.
        seqs = [e.sequence for e in self.timeline.events]
        if len(seqs) != len(set(seqs)):
            raise ValueError("Universe timeline contains duplicate event sequence numbers.")
        return self

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_character(self, char_id: str) -> Character | None:
        """Return the Character with the given ID, or ``None`` if absent."""
        return next((c for c in self.characters if c.id == char_id), None)

    def get_location(self, loc_id: str) -> Location | None:
        """Return the Location with the given ID, or ``None`` if absent."""
        return next((loc for loc in self.locations if loc.id == loc_id), None)

    def get_object(self, obj_id: str) -> Object | None:
        """Return the Object with the given ID, or ``None`` if absent."""
        return next((o for o in self.objects if o.id == obj_id), None)

    def get_timeline_event(self, evt_id: str) -> TimelineEvent | None:
        """Return the TimelineEvent with the given ID, or ``None`` if absent."""
        return next((e for e in self.timeline.events if e.id == evt_id), None)
