"""
Character data models for Headcanon.

A Character is a canonical definition of a fictional entity extracted by the
Universe Builder.  Characters are **immutable** canonical definitions; their
mutable runtime properties (location, emotion, inventory …) live exclusively
in the World State.

Reference: docs/universe/2_characters.md, docs/universe/1_universe_schema §6
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class CharacterRole(StrEnum):
    """Narrative role of the character within the universe."""

    PROTAGONIST = "Protagonist"
    SUPPORTING = "Supporting"
    MENTOR = "Mentor"
    VILLAIN = "Villain"
    MERCHANT = "Merchant"
    CIVILIAN = "Civilian"
    STUDENT = "Student"
    CREATURE = "Creature"
    COMPANION = "Companion"


class Temperament(StrEnum):
    """Stable personality temperament of the character."""

    CALM = "Calm"
    STOIC = "Stoic"
    IMPULSIVE = "Impulsive"
    AGGRESSIVE = "Aggressive"
    RESERVED = "Reserved"
    CHEERFUL = "Cheerful"
    SERIOUS = "Serious"


class HumorStyle(StrEnum):
    """General humour style expressed in dialogue."""

    DRY = "Dry"
    SARCASTIC = "Sarcastic"
    PLAYFUL = "Playful"
    NONE = "None"


class ConfidenceLevel(StrEnum):
    """General self-confidence level."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class SpeechTone(StrEnum):
    """Dominant tone of the character's speech."""

    ACADEMIC = "Academic"
    FORMAL = "Formal"
    FRIENDLY = "Friendly"
    BLUNT = "Blunt"
    COLD = "Cold"
    QUIET = "Quiet"
    ENERGETIC = "Energetic"


class VocabularyLevel(StrEnum):
    """Vocabulary complexity used in dialogue."""

    SIMPLE = "Simple"
    AVERAGE = "Average"
    ADVANCED = "Advanced"
    TECHNICAL = "Technical"


class SentenceLength(StrEnum):
    """Typical sentence length in dialogue."""

    SHORT = "Short"
    MEDIUM = "Medium"
    LONG = "Long"


class Formality(StrEnum):
    """Level of formality in speech."""

    FORMAL = "Formal"
    NEUTRAL = "Neutral"
    INFORMAL = "Informal"


class MoralAlignment(StrEnum):
    """D&D-style moral alignment."""

    LAWFUL_GOOD = "Lawful Good"
    NEUTRAL_GOOD = "Neutral Good"
    CHAOTIC_GOOD = "Chaotic Good"
    LAWFUL_NEUTRAL = "Lawful Neutral"
    TRUE_NEUTRAL = "True Neutral"
    CHAOTIC_NEUTRAL = "Chaotic Neutral"
    LAWFUL_EVIL = "Lawful Evil"
    NEUTRAL_EVIL = "Neutral Evil"
    CHAOTIC_EVIL = "Chaotic Evil"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class EntityMetadata(BaseModel, frozen=True):
    """
    Shared metadata block attached to every universe entity.

    Attributes:
        first_appearance: Chapter or event ID where the entity first appears.
        last_appearance:  Latest canon appearance.  ``None`` if ongoing.
        importance:       Relative importance in the universe (1–100).
        confidence:       Extraction confidence assigned by Universe Builder (0.0–1.0).
    """

    first_appearance: str | None = None
    last_appearance: str | None = None
    importance: int = Field(default=50, ge=1, le=100)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class CharacterPersonality(BaseModel, frozen=True):
    """
    Immutable personality definition.

    Personality never changes through gameplay.  Emotions and experiences
    influence *delivery*, not the underlying personality.

    Attributes:
        traits:      Core personality traits (e.g. ``["Intelligent", "Brave"]``).
        strengths:   Natural strengths (e.g. ``["Research", "Leadership"]``).
        weaknesses:  Natural flaws (e.g. ``["Perfectionism"]``).
        fears:       Persistent fears (e.g. ``["Failure"]``).
        values:      Core beliefs (e.g. ``["Justice", "Knowledge"]``).
        temperament: Broad temperament category.
        humor:       Humour style expressed in dialogue.
        confidence:  General self-confidence level.
    """

    traits: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    temperament: Temperament | None = None
    humor: HumorStyle | None = None
    confidence: ConfidenceLevel | None = None


class CharacterSpeech(BaseModel, frozen=True):
    """
    Speech profile that controls dialogue style.

    Speech remains mostly constant; current emotions influence *delivery*,
    not the speaking style defined here.

    Attributes:
        tone:            Dominant tone.
        vocabulary:      Vocabulary complexity.
        sentence_length: Typical sentence length.
        formality:       Level of formality.
        catchphrases:    Recurring phrases used by the character.
        quirks:          Distinctive verbal habits.
    """

    tone: SpeechTone | None = None
    vocabulary: VocabularyLevel | None = None
    sentence_length: SentenceLength | None = None
    formality: Formality | None = None
    catchphrases: list[str] = Field(default_factory=list)
    quirks: list[str] = Field(default_factory=list)


class CharacterGoal(BaseModel, frozen=True):
    """
    A long-term character motivation.

    Attributes:
        id:       Unique goal identifier (e.g. ``"goal_stop_voldemort"``).
        title:    Human-readable description of the goal.
        priority: Priority score (higher = more important).
    """

    id: str
    title: str
    priority: int = Field(ge=0, le=100)


class CharacterMorality(BaseModel, frozen=True):
    """
    Moral framework governing decision-making.

    Attributes:
        alignment: D&D-style alignment string.
        laws:      Personal rules the character follows.
        taboos:    Actions the character refuses to perform.
    """

    alignment: MoralAlignment | None = None
    laws: list[str] = Field(default_factory=list)
    taboos: list[str] = Field(default_factory=list)


class CharacterAbility(BaseModel, frozen=True):
    """
    A discrete skill or power possessed by the character.

    Attributes:
        id:          Unique ability identifier (e.g. ``"spell_expelliarmus"``).
        name:        Human-readable ability name.
        description: Brief description of what the ability does.
    """

    id: str
    name: str
    description: str = ""


class CharacterAppearance(BaseModel, frozen=True):
    """
    Visual attributes used by the Media Pipeline for image generation.

    These fields are descriptive only and must never be used for reasoning.

    Attributes:
        hair:     Hair description.
        eyes:     Eye colour / description.
        height:   Height (e.g. ``"165 cm"``).
        clothing: Default clothing description.
    """

    hair: str | None = None
    eyes: str | None = None
    height: str | None = None
    clothing: str | None = None


class CharacterKnowledge(BaseModel, frozen=True):
    """
    What the character is *capable* of knowing.

    This defines the character's knowledge scope, NOT their current memories.
    The Character Engine may only reason within this scope.

    Attributes:
        known_locations: Location IDs the character is aware of.
        known_people:    Character IDs the character knows.
        known_events:    Event IDs the character knows about.
        known_objects:   Object IDs the character is aware of.
        scope:           High-level topic categories (e.g. ``["Magic", "Potions"]``).
    """

    known_locations: list[str] = Field(default_factory=list)
    known_people: list[str] = Field(default_factory=list)
    known_events: list[str] = Field(default_factory=list)
    known_objects: list[str] = Field(default_factory=list)
    scope: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class Character(BaseModel, frozen=True):
    """
    Canonical definition of a fictional character within the universe.

    Characters store *who they are*, never *what they are doing*.  Mutable
    runtime state (location, emotion, inventory, etc.) belongs in the
    World State.

    ID convention: ``char_<name>``  (e.g. ``char_harry``, ``char_hermione``).

    Attributes:
        id:            Immutable unique character identifier.
        name:          Canonical full name.
        aliases:       Alternative names used for entity resolution.
        role:          Narrative role within the universe.
        species:       Species or race (e.g. ``"Human"``, ``"Elf"``).
        age:           Canonical age; ``None`` if unknown.
        occupation:    Primary occupation or title.
        description:   Concise canonical description (not a narrative summary).
        appearance:    Visual attributes for media generation.
        personality:   Immutable personality definition.
        speech:        Immutable speech profile.
        morality:      Moral framework and personal laws.
        goals:         Long-term motivations ordered by priority.
        knowledge:     Knowledge scope (what the character *can* know).
        abilities:     Discrete skills and powers.
        metadata:      Shared entity metadata.
    """

    id: str = Field(pattern=r"^char_\S+$")
    name: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    role: CharacterRole | None = None
    species: str | None = None
    age: int | None = Field(default=None, ge=0)
    occupation: str | None = None
    description: str = ""
    appearance: CharacterAppearance = Field(default_factory=CharacterAppearance)
    personality: CharacterPersonality = Field(default_factory=CharacterPersonality)
    speech: CharacterSpeech = Field(default_factory=CharacterSpeech)
    morality: CharacterMorality = Field(default_factory=CharacterMorality)
    goals: list[CharacterGoal] = Field(default_factory=list)
    knowledge: CharacterKnowledge = Field(default_factory=CharacterKnowledge)
    abilities: list[CharacterAbility] = Field(default_factory=list)
    metadata: EntityMetadata = Field(default_factory=EntityMetadata)

    @field_validator("aliases")
    @classmethod
    def aliases_are_unique(cls, v: list[str]) -> list[str]:
        """Reject duplicate alias entries."""
        if len(v) != len(set(v)):
            raise ValueError("Character aliases must be unique.")
        return v

    @field_validator("abilities")
    @classmethod
    def ability_ids_are_unique(cls, v: list[CharacterAbility]) -> list[CharacterAbility]:
        """Reject duplicate ability IDs."""
        ids = [a.id for a in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Ability IDs must be unique within a character.")
        return v

    @field_validator("goals")
    @classmethod
    def goal_ids_are_unique(cls, v: list[CharacterGoal]) -> list[CharacterGoal]:
        """Reject duplicate goal IDs."""
        ids = [g.id for g in v]
        if len(ids) != len(set(ids)):
            raise ValueError("Goal IDs must be unique within a character.")
        return v

    @model_validator(mode="after")
    def self_reference_not_in_knowledge(self) -> Character:
        """
        A character's own ID must not appear in known_people to prevent
        trivial self-references that pollute relationship graphs.
        """
        if self.id in self.knowledge.known_people:
            raise ValueError(
                f"Character '{self.id}' must not list itself in knowledge.known_people."
            )
        return self
