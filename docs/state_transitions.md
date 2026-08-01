# State Transitions

## Purpose

This document defines how the persistent world evolves in response to user actions and simulation events.

Every state transition must preserve narrative consistency and world rules.

The World State is the only mutable representation of a universe.

---

# State Categories

The World State consists of:

- Character States
- Location States
- Object States
- Relationship States
- Timeline States
- Event States
- Scene State
- Global World State

---

# Character State

A character's state may change through:

- Conversations
- Actions
- Combat
- Travel
- Story Events
- Simulation

Mutable properties include:

- Current Location
- Emotional State
- Inventory
- Active Goal
- Memories
- Relationships
- Health / Status

---

# Location State

A location changes when:

- Characters enter or leave
- Objects move
- Events occur
- Environmental changes happen

Mutable properties:

- Occupants
- Objects Present
- Active Events
- Environment
- Accessibility

---

# Object State

Objects may transition between:

- Locations
- Owners
- Conditions

Examples

Intact → Broken

Hidden → Discovered

Owned → Dropped

Locked → Unlocked

---

# Relationship State

Relationships evolve through interaction.

Possible transitions:

Neutral

↓

Friendly

↓

Trusted

↓

Close

or

Neutral

↓

Hostile

↓

Enemy

Relationship values should change gradually.

---

# Emotion State

Possible emotional changes include:

Calm

↓

Curious

↓

Happy

↓

Excited

↓

Angry

↓

Fearful

↓

Desperate

↓

Relieved

Transitions depend on simulation outcomes.

---

# Timeline State

Events move through:

Pending

↓

Active

↓

Completed

or

Pending

↓

Cancelled

or

Pending

↓

Modified

Simulation may generate new future events.

---

# Scene State

The current scene changes when:

- User travels
- Time advances
- Characters move
- Objects move
- Events trigger

A new scene is generated after every valid state update.

---

# Invalid Transitions

The system must reject transitions that violate:

- World Rules
- Character Knowledge
- Timeline Consistency
- Physical Constraints
- Universe Canon

---

# Persistence

After every successful transition:

1. Update World State
2. Update Memories
3. Update Relationships
4. Update Timeline
5. Save Snapshot
6. Refresh Scene

---

# Related Documents

- runtime_pipeline.md
- universe/09_world_state.md
- engines/04_simulation_engine.md
- engines/08_timeline_engine.md