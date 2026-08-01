# Memory Schema

## Purpose

The Memory System enables characters to retain experiences, form opinions, and evolve naturally over time.

Rather than storing conversation history, the system stores meaningful memories that influence future decisions, relationships, emotions, and dialogue.

Every character maintains an independent memory bank.

---

# Responsibilities

The Memory System is responsible for

- Recording significant experiences
- Updating character knowledge
- Influencing dialogue
- Affecting relationships
- Supporting long-term persistence
- Providing context to the Character Engine

---

# Memory Principles

Memories should be

- Persistent
- Character-specific
- Chronological
- Searchable
- Weighted by importance

Not every interaction becomes a memory.

Only meaningful experiences should be stored.

---

# Memory Structure

Each memory contains

- Memory ID
- Character ID
- Timestamp
- Event ID (optional)
- Memory Type
- Summary
- Emotional Impact
- Importance
- Participants
- Location
- Related Objects
- Tags

---

# Memory Types

Possible memory categories include

- Conversation
- Observation
- Discovery
- Gift
- Conflict
- Victory
- Defeat
- Travel
- Relationship Change
- World Event

Additional categories may be introduced as the simulation evolves.

---

# Importance

Every memory has an importance score.

Range

0 – 100

Examples

5

Minor conversation

25

Interesting observation

60

Receiving a valuable gift

90

Witnessing a major battle

100

Death of a close friend

Higher importance memories are prioritised during retrieval.

---

# Emotional Impact

Each memory stores its emotional significance.

Possible emotions

- Happy
- Sad
- Angry
- Curious
- Fearful
- Hopeful
- Proud
- Guilty
- Relieved
- Neutral

Multiple emotions may be associated with a single memory.

---

# Memory Retrieval

When generating character responses, memories are selected based on

- Relevance to the current interaction
- Importance
- Recency
- Emotional similarity
- Related characters
- Related objects
- Current goals

The Character Engine should retrieve only the most relevant memories rather than the entire memory history.

---

# Memory Creation

A new memory may be created after

- Meaningful conversation
- Major event
- Relationship change
- Receiving or losing an item
- Completing a goal
- Witnessing an important event

Routine actions should not automatically create memories.

---

# Memory Updates

Existing memories may be updated when

- New information changes previous understanding
- Emotional significance evolves
- Relationships change
- Canon events are altered

The original event remains preserved.

---

# Forgetting

Characters may gradually deprioritise insignificant memories.

Low-importance memories remain stored but are retrieved less frequently.

Critical memories should never be forgotten.

---

# Memory Validation

Every memory must reference

- A valid character
- Valid participants (if any)
- A valid location (if applicable)
- Existing objects (if referenced)

Invalid references should be rejected.

---

# Persistence

Character memories are saved

- After important interactions
- After simulation events
- During autosave
- During snapshot creation

Memories are restored whenever a universe is loaded.

---

# Design Principles

The Memory System should

- Simulate long-term memory
- Avoid storing raw chat logs
- Preserve narrative consistency
- Influence future behaviour naturally
- Scale efficiently for long-running universes

---

# Related Documents

- 09_world_state.md
- 10_events.md
- 14_emotion_schema.md
- ../engines/06_memory_engine.md
- ../engines/02_character_engine.md