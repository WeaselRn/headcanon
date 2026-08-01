---

# State Mutation Rules

This document defines which engine owns which part of the system state.

Only the owning engine may directly modify a state component.

All other engines must treat that state as read-only.

This ensures predictable execution and prevents conflicting updates.

---

# Mutation Principles

The following rules apply globally.

- Every mutable field has exactly one owner.
- Engines may read any state but only modify owned state.
- Canonical Universe data is immutable after creation.
- Runtime modifications occur only within World State.
- Engines communicate through Runtime Pipeline outputs.
- No engine may directly modify another engine's owned state.

---

# Universe Builder

## CAN MODIFY

- Universe
- Metadata
- Characters
- Locations
- Objects
- Relationships
- Timeline
- World Rules
- Knowledge Graph
- Initial World State

## CANNOT MODIFY

- Existing World State
- Character Memories
- Relationships after runtime
- Scene
- Runtime Events

---

# Interaction Engine

## CAN MODIFY

- Interaction Context

## CANNOT MODIFY

- World State
- Timeline
- Character Memory
- Relationships
- Inventory
- Character Position

Interaction Engine only interprets user intent.

---

# Character Engine

## CAN MODIFY

- Character Response
- Dialogue
- Internal Character Reasoning

## CANNOT MODIFY

- Character Location
- Inventory
- Timeline
- Events
- World Rules

Character Engine produces responses only.

It never changes the world.

---

# Memory Engine

## CAN MODIFY

- Character Memories
- Memory Importance
- Memory References
- Memory Retrieval Cache

## CANNOT MODIFY

- Character Personality
- Timeline
- World Rules
- Character Position
- Inventory

Memory Engine only changes memories.

---

# Relationship Engine

## CAN MODIFY

- Affinity
- Trust
- Respect
- Fear
- Rivalry
- Friendship

## CANNOT MODIFY

- Character Dialogue
- Timeline
- Character Position
- Inventory
- Events

---

# Simulation Engine

## CAN MODIFY

- Character Positions
- Object Positions
- Inventory
- NPC Actions
- Active Events
- Environmental State
- World Flags

## CANNOT MODIFY

- Personality
- Speech Style
- Canon Universe
- World Rules

Simulation Engine owns world changes.

---

# Timeline Engine

## CAN MODIFY

- Current Time
- Event Status
- Completed Events
- Scheduled Events
- Timeline Position

## CANNOT MODIFY

- Character Personality
- Relationships
- Memories
- Inventory

Timeline Engine owns temporal progression.

---

# Scene Engine

## CAN MODIFY

- Scene Object
- Visible Characters
- Visible Objects
- Available Actions
- Scene Description

## CANNOT MODIFY

- World State
- Timeline
- Memories
- Relationships

Scene Engine is a renderer.

It never changes simulation data.

---

# Narration Engine

## CAN MODIFY

- Narration
- Dialogue Formatting
- Scene Description

## CANNOT MODIFY

- World State
- Timeline
- Memories
- Relationships
- Character Data

Narration is presentation only.

---

# Media Pipeline

## CAN MODIFY

- Generated Images
- Narration Audio
- Ambient Audio
- Metadata
- Asset Storage

## CANNOT MODIFY

- Universe
- World State
- Character Data
- Timeline

Media generation never changes gameplay.

---

# World State Ownership

| World State Component | Owner |
|------------------------|-------|
| Character Position | Simulation Engine |
| Character Emotion | Character Engine |
| Character Memories | Memory Engine |
| Relationships | Relationship Engine |
| Inventory | Simulation Engine |
| Current Time | Timeline Engine |
| Active Events | Simulation Engine |
| Future Events | Timeline Engine |
| Scene | Scene Engine |
| Narration | Narration Engine |
| Images | Media Pipeline |

---

# Mutation Order

Every interaction follows this ownership order.

```
Interaction

↓

Character

↓

Memory

↓

Relationship

↓

Simulation

↓

Timeline

↓

Scene

↓

Narration

↓

Media

↓

Persist
```

No engine may modify state after persistence.

---

# Conflict Resolution

If two engines attempt to modify the same state,

the owner always wins.

Example

Character Engine attempts to move Hermione.

Rejected.

Simulation Engine owns character movement.

Example

Simulation Engine attempts to change Hermione's personality.

Rejected.

Universe data is immutable.

---

# Immutable Data

The following data may never change during runtime.

- Character personality
- Character speech style
- Canon timeline
- World rules
- Knowledge graph
- Metadata
- Universe identifiers

Changes require rebuilding the Universe.

---

# Summary

The State Mutation Rules ensure that every mutable field has a single owner.

This prevents conflicting updates, simplifies debugging, and guarantees deterministic execution across all Headcanon engines.

All future engines must declare their ownership before modifying any new state component.