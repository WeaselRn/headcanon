# World State

## Purpose

The World State represents the live, mutable version of a reconstructed universe.

While the Universe Model stores the canonical structure extracted from the source story, the World State stores everything that changes as users interact with the universe.

Every interaction, simulation, event, or decision updates the World State.

It is the primary source of truth during runtime.

---

# Responsibilities

The World State is responsible for:

- Tracking all mutable entities
- Maintaining character locations
- Tracking inventories
- Updating relationships
- Recording emotional changes
- Managing active events
- Advancing the timeline
- Providing the current scene
- Supporting save and restore

---

# Relationship with Universe Model

Universe Model

- Static
- Created once
- Canonical
- Never modified

↓

World State

- Dynamic
- Updated continuously
- Represents current reality

---

# Components

The World State consists of

- Current Time
- Active Scene
- Character States
- Location States
- Object States
- Relationship States
- Active Events
- Pending Events
- Timeline Progress
- Global Variables

---

# Character States

Each character contains

- Character ID
- Current Location
- Emotional State
- Inventory
- Active Goal
- Current Activity
- Memories
- Relationships
- Health / Status

Example

Harry Potter

Location:
Great Hall

Emotion:
Curious

Inventory:
Wand
Marauder's Map

Current Goal:
Find Hermione

---

# Location States

Each location stores

- Characters Present
- Objects Present
- Environmental State
- Current Events
- Accessibility

Example

Great Hall

Characters

- Harry
- Hermione
- Draco

Objects

- Tables
- Food
- Owl Post

Environment

Morning

Accessible

Yes

---

# Object States

Objects maintain

- Current Owner
- Current Location
- Condition
- Visibility
- Interaction State

Examples

Sword

Owner:
User

Condition:
Intact

Visibility:
Equipped

---

# Relationship States

Relationships are mutable.

Stored as

Character A

↓

Character B

↓

Relationship Value

↓

Trust

↓

Affinity

↓

Respect

↓

Fear

Relationship values change through simulation.

---

# Active Events

Events currently affecting the world.

Each event stores

- Event ID
- Participants
- Location
- Trigger
- Current Status
- Expected Outcome

---

# Pending Events

Future events waiting for activation.

Examples

- Hogwarts Feast
- Quidditch Match
- Dragon Attack

Simulation determines whether they occur.

---

# Timeline Progress

Tracks

Current Chapter

Current Day

Current Time

Completed Events

Cancelled Events

Generated Events

---

# Global Variables

Universe-wide information

Examples

Current Weather

Season

Time of Day

Political State

War Status

Magic Stability

---

# State Updates

Every successful interaction follows:

User Action

↓

Simulation

↓

State Update

↓

Scene Refresh

↓

Autosave

---

# Consistency Rules

The World State must always satisfy

- One character cannot exist in multiple locations.
- One object cannot have multiple owners.
- Timeline remains chronological.
- World rules are never violated.
- All references remain valid.

---

# Persistence

The World State is saved

- After interactions
- After simulations
- Before media generation
- Before session exit
- During automatic checkpoints

Snapshots are versioned and stored separately.

---

# Related Documents

- 01_universe_schema.md
- 07_timeline.md
- 10_events.md
- 11_inventory.md
- 15_snapshot_schema.md
- ../engines/04_simulation_engine.md
- ../engines/08_timeline_engine.md


---

# `docs/universe/09_world_state.md`

## Goal

This document defines the **live simulation state** of a universe.

Think of it like this:

```
Universe
    ↓
Blueprint (mostly immutable)

↓

WorldState
    ↓
Current save file
```

The Universe defines **what exists**.

The WorldState defines **what is happening right now.**

---

# Structure

```text
# World State

Version

Status

Owner

────────────────────────────

1. Purpose

2. Design Philosophy

3. WorldState Object

4. Time System

5. Scene State

6. Character State

7. Location State

8. Object State

9. Active Events

10. Pending Events

11. Environmental State

12. World Flags

13. Save Format

14. Update Rules

15. State Lifecycle

16. Example World State
```

---

# 1. Purpose

Explain

> WorldState represents the current live simulation.

Unlike Universe

WorldState changes after almost every interaction.

Example

```
Universe

Hermione is intelligent.

↓

WorldState

Hermione is currently in the Library,
reading a book,
slightly annoyed,
holding an old diary.
```

---

# 2. Design Philosophy

Rules

```
Universe never changes.

↓

WorldState changes continuously.

↓

WorldState references Universe IDs.

↓

No duplicated immutable information.

↓

Everything must be serializable.

↓

Everything can be restored.
```

---

# 3. WorldState Object

Root JSON

```json
{
    "time": {},
    "scene": {},
    "characters": {},
    "locations": {},
    "objects": {},
    "relationships": {},
    "events": {},
    "environment": {},
    "flags": {}
}
```

Notice

Characters is now

```json
{
    "char_harry":{}
}
```

not an array.

Makes lookup O(1).

---

# 4. Time System

Example

```json
{
    "day":3,
    "hour":15,
    "minute":20,
    "season":"Autumn",
    "weather":"Rain",
    "timeline_position":"evt_041"
}
```

Every engine references this.

Simulation advances it.

---

# 5. Scene State

Current visible scene.

Example

```json
{
    "scene_id":"scene_library",
    "location":"loc_library",
    "visible_characters":[
        "char_harry",
        "char_hermione"
    ],
    "visible_objects":[
        "obj_book"
    ],
    "available_actions":[]
}
```

Frontend renders this directly.

---

# 6. Character State

Do NOT duplicate Character schema.

Only mutable values.

Example

```json
{
    "char_hermione":{
        "location":"loc_library",
        "emotion":"Focused",
        "health":"Healthy",
        "inventory":[
            "obj_book"
        ],
        "current_goal":"Research",
        "active_memories":[
            "mem_031"
        ],
        "current_action":"Reading"
    }
}
```

Everything here can change.

---

# 7. Location State

Example

```json
{
    "loc_library":{
        "occupants":[
            "char_harry",
            "char_hermione"
        ],
        "objects":[
            "obj_book"
        ],
        "status":"Open"
    }
}
```

---

# 8. Object State

Example

```json
{
    "obj_book":{
        "owner":"char_hermione",
        "location":"loc_library",
        "condition":"Good",
        "hidden":false
    }
}
```

---

# 9. Active Events

Events currently occurring.

Example

```json
[
    {
        "id":"evt_library",
        "status":"active",
        "participants":[]
    }
]
```

---

# 10. Pending Events

Future scheduled events.

Example

```
Dinner

↓

Starts

↓

18:00
```

Simulation checks these.

---

# 11. Environment

Example

```json
{
    "weather":"Rain",
    "temperature":17,
    "lighting":"Dim",
    "noise":"Quiet"
}
```

---

# 12. World Flags

Very useful.

Example

```json
{
    "quest_started":true,
    "door_open":false,
    "dragon_dead":true
}
```

Flags are simple booleans or enums.

---

# 13. Save Format

WorldState stored as

```
world_state.json
```

Snapshots

```
snapshot_001.json

snapshot_002.json

snapshot_003.json
```

Universe never duplicated.

---

# 14. Update Rules

Very important.

Example

```
Character Engine

updates

emotion

knowledge

↓

Simulation Engine

updates

location

inventory

events

↓

Relationship Engine

updates

trust

respect

↓

Timeline Engine

updates

time
```

Each engine owns specific fields.

---

# 15. State Lifecycle

Document

```
User Action

↓

Character Response

↓

Simulation

↓

Memory Update

↓

Relationship Update

↓

Timeline Advance

↓

Persist WorldState

↓

Generate Scene
```

Exactly this order.

---

# 16. Example WorldState

A complete small example.

```
Village

↓

Morning

↓

Hero in Tavern

↓

Merchant nearby

↓

Sword on table

↓

Quest active
```

Show the full JSON.

---

