"""
Emotion data models for Headcanon.

The Emotion System represents the **current** emotional state of a character.
Unlike memories (which are persistent), emotions are temporary and continuously
evolve as the simulation progresses.

Emotions influence dialogue tone, decision making, relationships, and reactions
to events.  They must never override a character's established personality
traits.

Reference: docs/universe/14_emotion_schema.md
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class EmotionCategory(StrEnum):
    """
    Predefined emotion vocabulary.

    Grouped loosely as Positive, Neutral, or Negative for readability;
    the simulation engine determines valid transitions between states.
    """

    # Positive
    HAPPY = "Happy"
    EXCITED = "Excited"
    CURIOUS = "Curious"
    HOPEFUL = "Hopeful"
    PROUD = "Proud"
    RELIEVED = "Relieved"
    CONFIDENT = "Confident"

    # Neutral
    CALM = "Calm"
    FOCUSED = "Focused"
    TIRED = "Tired"
    INDIFFERENT = "Indifferent"

    # Negative
    ANGRY = "Angry"
    SAD = "Sad"
    FEARFUL = "Fearful"
    GUILTY = "Guilty"
    JEALOUS = "Jealous"
    CONFUSED = "Confused"
    FRUSTRATED = "Frustrated"
    LONELY = "Lonely"


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class EmotionState(BaseModel):
    """
    The current emotional state of a single character.

    Every character has exactly one primary emotion at any given moment.  The
    intensity modulates the *degree* of that emotion (0 = barely perceptible,
    100 = overwhelming).

    Attributes:
        character_id:      ID of the character whose emotion is recorded.
        current_emotion:   Primary active emotion.
        intensity:         Intensity score (0–100).
        previous_emotion:  Emotion active immediately before the current one.
        trigger:           Human-readable description of what caused the change
                           (e.g. ``"User insulted Draco"``).
        last_updated:      UTC datetime when this state was last modified.
    """

    character_id: str = Field(min_length=1)
    current_emotion: EmotionCategory = EmotionCategory.CALM
    intensity: int = Field(default=50, ge=0, le=100)
    previous_emotion: EmotionCategory | None = None
    trigger: str | None = None
    last_updated: datetime | None = None
