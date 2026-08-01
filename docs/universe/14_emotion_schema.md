# Emotion Schema

## Purpose

The Emotion System represents the current emotional state of every character in the universe.

Emotions influence dialogue, decision making, relationships, goals, and reactions to events.

Unlike memories, emotions are temporary and continuously evolve as the simulation progresses.

---

# Responsibilities

The Emotion System is responsible for

- Tracking current emotions
- Updating emotions after events
- Influencing dialogue generation
- Affecting character behaviour
- Supporting realistic emotional transitions

---

# Core Principles

Emotions should be

- Dynamic
- Character-specific
- Context-aware
- Influenced by memories
- Influenced by relationships
- Influenced by world events

Characters should never behave identically regardless of emotion.

---

# Emotion Structure

Each character stores

- Current Emotion
- Emotional Intensity
- Previous Emotion
- Emotional Trigger
- Last Updated Timestamp

---

# Emotion Categories

Supported emotions include

Positive

- Happy
- Excited
- Curious
- Hopeful
- Proud
- Relieved
- Confident

Neutral

- Calm
- Focused
- Tired
- Indifferent

Negative

- Angry
- Sad
- Fearful
- Guilty
- Jealous
- Confused
- Frustrated
- Lonely

Additional emotions may be added as needed.

---

# Emotional Intensity

Every emotion has an intensity.

Range

0 – 100

Examples

10

Slight curiosity

35

Annoyed

60

Very happy

80

Extremely angry

100

Complete panic

Intensity affects dialogue tone and behaviour.

---

# Emotional Triggers

Emotions may change due to

- Conversations
- Gifts
- Arguments
- Discoveries
- World events
- Combat
- Loss
- Achievements
- Relationship changes
- Goal completion

---

# Emotional Transitions

Typical progression

Calm

↓

Curious

↓

Excited

↓

Relieved

or

Calm

↓

Annoyed

↓

Angry

↓

Furious

↓

Exhausted

The Simulation Engine determines valid transitions.

---

# Emotion Decay

Not all emotions persist indefinitely.

Over time

High intensity

↓

Medium intensity

↓

Low intensity

↓

Neutral

unless reinforced by new events.

---

# Relationship Influence

Relationships affect emotional responses.

Examples

A trusted friend leaving

↓

Sad

An enemy leaving

↓

Relieved

The same event may produce different emotions depending on the relationship.

---

# Memory Influence

Important memories influence emotions.

Examples

Past betrayal

↓

Distrust

Receiving a meaningful gift

↓

Happiness

Witnessing danger

↓

Fear

Recent high-priority memories should have greater influence.

---

# Dialogue Influence

The Character Engine should adjust

- Tone
- Vocabulary
- Response length
- Politeness
- Confidence
- Decision making

based on the current emotional state.

---

# Behaviour Influence

Emotion affects actions.

Examples

Curious

↓

Investigate

Fearful

↓

Avoid danger

Angry

↓

Confront

Happy

↓

Socialise

Focused

↓

Continue current goal

---

# Validation

Every character must have

- Exactly one primary current emotion
- A valid intensity
- A valid trigger
- A timestamp

---

# Persistence

Emotional state is saved

- After interactions
- After simulation updates
- During autosave
- During snapshot creation

Emotions are restored when the universe is reloaded.

---

# Design Principles

The Emotion System should

- Produce believable reactions
- Avoid abrupt emotional changes
- Reinforce narrative consistency
- Work together with memories and relationships
- Never override established personality traits

---

# Related Documents

- 13_memory_schema.md
- 06_relationships.md
- 09_world_state.md
- ../engines/02_character_engine.md
- ../engines/06_memory_engine.md
- ../engines/07_relationship_engine.md