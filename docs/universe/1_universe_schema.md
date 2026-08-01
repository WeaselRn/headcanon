

# Universe Schema

**Version:** 1.0

**Status:** Draft

**Owner:** Headcanon Core Engine

---

# 1. Purpose

The Universe is the single source of truth for every Headcanon session.

Everything inside the application ultimately derives from the Universe.

The original story is **never** queried again after reconstruction.

Instead,

```
Story

↓

Universe

↓

World State

↓

Interaction

↓

Simulation

↓

Media
```

Once a universe has been built, every subsystem references it.

---

# 2. Design Principles

The Universe should satisfy these goals.

## 2.1 Persistence

The universe should survive across sessions.

Users leave.

Users return.

Nothing resets.

---

## 2.2 Determinism

Given the same universe and world state,

the same event should produce nearly identical outcomes.

Randomness should never replace consistency.

---

## 2.3 Canon Preservation

The reconstruction engine should preserve

* personalities
* relationships
* lore
* world mechanics
* speech styles
* motivations

without inventing unnecessary information.

---

## 2.4 Separation of Static and Dynamic Data

The original story defines

```
Static Universe
```

User interactions define

```
Dynamic World State
```

Never mix them.

---

# 3. High-Level Architecture

```
Universe
│
├── Metadata
│
├── Canon
│
├── Characters
│
├── Locations
│
├── Objects
│
├── Timeline
│
├── Relationships
│
├── Rules
│
├── Knowledge Graph
│
├── World State
│
├── Memories
│
├── Generated Assets
│
└── Provenance
```

Every engine reads from this object.

---

# 4. Universe Lifecycle

```
Import Story

↓

Extract Text

↓

Universe Builder

↓

Universe JSON

↓

Validation

↓

Persist

↓

Interactive Session

↓

World Updates

↓

Save Snapshot
```

---

# 5. Universe Object

```json
{
  "metadata": {},
  "canon": {},
  "characters": [],
  "locations": [],
  "objects": [],
  "timeline": [],
  "relationships": [],
  "rules": [],
  "knowledge_graph": {},
  "world_state": {},
  "generated_assets": [],
  "provenance": {}
}
```

Everything references this root object.

---

# 6. Metadata

Metadata describes the universe itself.

Example

```json
{
  "id": "hp_001",
  "title": "Harry Potter and the Philosopher's Stone",
  "author": "J. K. Rowling",
  "source": "PDF",
  "language": "English",
  "version": 1,
  "created_at": "...",
  "updated_at": "...",
  "llm": "Gemini 2.5 Flash"
}
```

Metadata never affects simulation.

It exists for storage and provenance.

---

# 7. Canon

Canon stores immutable information extracted from the original work.

Example

```json
{
  "genre": "Fantasy",
  "setting": "Wizarding World",
  "era": "1991",
  "themes": [
    "Friendship",
    "Courage",
    "Sacrifice"
  ]
}
```

Canon never changes.

---

# 8. Characters

Characters contain every actor capable of making decisions.

Example

```json
{
    "id": "char_harry",
    "name": "Harry Potter",
    "role": "Protagonist"
}
```

Detailed specification lives in

```
characters.md
```

---

# 9. Locations

Every physical place inside the world.

Example

```json
{
    "id":"great_hall",
    "name":"Great Hall"
}
```

Detailed later.

---

# 10. Objects

Every significant item.

Example

```json
{
    "id":"elder_wand",
    "owner":"Harry",
    "location":"Headmaster Office"
}
```

---

# 11. Timeline

Chronological sequence of every important event.

Example

```json
[
    {
        "event":"Harry receives Hogwarts letter",
        "day":1
    }
]
```

Timeline is mutable.

Original events remain stored.

Modified events are appended.

---

# 12. Relationships

Graph representing how entities feel about one another.

Example

```json
{
    "source":"Harry",
    "target":"Hermione",
    "value":95
}
```

---

# 13. Rules

Rules define immutable mechanics.

Example

```
Magic requires a wand.

Muggles cannot naturally perform magic.

Time travel obeys Time Turner rules.
```

Simulation Engine must never violate them.

---

# 14. Knowledge Graph

Represents every connection inside the universe.

Example

```
Harry

↓

owns

↓

Nimbus 2000

↓

stored in

↓

Dormitory
```

Knowledge graph enables reasoning.

---

# 15. World State

This is the only mutable portion.

Contains

```
Current locations

Current inventories

Current weather

Current relationships

Current emotions

Current objectives

Current active events
```

Unlike Characters,

World State changes every interaction.

---

# 16. Generated Assets

Every media file belongs here.

Example

```json
{
    "scene":"Arrival at Hogwarts",
    "image":"scene12.png",
    "audio":"scene12.mp3",
    "created":"..."
}
```

---

# 17. Provenance

Tracks how the universe evolved.

Example

```json
{
    "snapshot":14,
    "reason":"User convinced Ron to leave Hogwarts.",
    "changed_by":"Simulation Engine",
    "timestamp":"..."
}
```

Every mutation creates provenance.

Nothing changes silently.

---

# 18. Object References

Every entity must have a unique identifier.

Example

```
char_harry

char_ron

loc_hogwarts

obj_elderwand

evt_sorting

rule_magic
```

IDs never change.

Names may.

---

# 19. Cross References

Everything should reference IDs.

Good

```json
{
    "owner":"char_harry"
}
```

Bad

```json
{
    "owner":"Harry Potter"
}
```

Using IDs prevents ambiguity.

---

# 20. Validation Rules

Universe Builder must validate:

✔ Every character has a unique ID

✔ Every location exists

✔ Every relationship references valid characters

✔ Every event references valid entities

✔ Every object has one location

✔ Every graph edge is valid

Reject invalid universes.

---

# 21. Storage Layout

Recommended B2 layout

```
universes/

    hp_001/

        universe.json

        metadata.json

        snapshots/

            snapshot_0001.json

            snapshot_0002.json

        assets/

            images/

            audio/

            narration/

        provenance/

            changes.json
```

Universe is independent of generated media.

---

# 22. Update Flow

User

↓

Interaction Engine

↓

Simulation Engine

↓

World State Update

↓

Validation

↓

Snapshot

↓

Persist

The original Universe remains unchanged.

Only World State evolves.

---

# 23. Engine Responsibilities

Universe Builder

* Creates Universe

Character Engine

* Reads Characters

Interaction Engine

* Reads World State

Simulation Engine

* Updates World State

Media Engine

* Reads Scene

Storage Engine

* Saves snapshots

No engine owns the entire Universe.

Each engine owns only its domain.

---

# 24. Future Extensions

Universe schema intentionally supports future additions.

Possible modules

```
Politics

Economy

Weather

Quest System

NPC Scheduler

Crafting

Combat

Dialogue Trees

Faction Reputation

Achievements

Companions

Dynamic Ecosystem
```

These can be added without breaking the core schema.

---

# 25. Summary

The **Universe** is not a story.

It is a structured, persistent representation of a fictional world.

Every interaction, simulation, memory, relationship, timeline update, and media generation operates on this single source of truth.

This separation between **immutable canon** and **mutable world state** is the architectural foundation that allows Headcanon to transform static stories into living, evolving universes.
