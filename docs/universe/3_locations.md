# `docs/universe/03_locations.md`

---

# Locations

**Version:** 1.0

**Status:** Draft

**Owner:** World State Engine

---

# 1. Purpose

Locations define every explorable place inside a Headcanon universe.

A location is **not merely a background**. It is a persistent entity that contains:

* physical properties
* connected locations
* occupants
* objects
* atmosphere
* active events
* environmental rules

Every interaction in Headcanon occurs **inside a location**.

---

# 2. Design Philosophy

Locations should satisfy five principles.

## Persistent

A location always exists.

It is never recreated every interaction.

---

## Spatial

Locations define where characters and objects exist.

Nothing exists "nowhere."

---

## Interactive

Locations contain things users can observe and interact with.

---

## Dynamic

The physical description remains mostly constant.

Its contents constantly evolve.

---

## Canonical

Descriptions should faithfully match the source material.

---

# 3. Location Lifecycle

```text
Universe Builder

↓

Extract Locations

↓

Build Connections

↓

Initialize World State

↓

Characters Move

↓

Objects Move

↓

Events Trigger

↓

Save Snapshot
```

---

# 4. Location Object

```json
{
  "id": "",
  "name": "",
  "aliases": [],
  "description": "",
  "category": "",
  "region": "",
  "parent_location": "",
  "connections": [],
  "appearance": {},
  "environment": {},
  "occupants": [],
  "objects": [],
  "events": [],
  "rules": [],
  "metadata": {}
}
```

---

# 5. Identity

Every location has a permanent identifier.

Example

```json
{
    "id":"loc_great_hall",
    "name":"Great Hall"
}
```

IDs never change.

---

# 6. Categories

Example categories

```text
Building

Room

Forest

Village

Castle

Mountain

Planet

Dungeon

Spacecraft

Street

Ocean

Kingdom
```

Used for navigation and filtering.

---

# 7. Region

Locations belong to larger areas.

Example

```text
Great Hall

↓

Hogwarts Castle

↓

Scotland

↓

Wizarding World
```

---

# 8. Parent Location

Example

```json
{
    "parent_location":"loc_hogwarts_castle"
}
```

Enables hierarchical exploration.

---

# 9. Description

The description should represent the canonical appearance.

Example

```text
The enchanted ceiling reflects the sky above.

Four long tables stretch across the hall.

Floating candles illuminate the room.
```

Descriptions remain mostly immutable.

---

# 10. Appearance

Contains media-generation details.

Example

```json
{
    "architecture":"Gothic",

    "lighting":"Warm",

    "size":"Massive",

    "dominant_colors":[
        "Gold",
        "Brown"
    ]
}
```

Used by the Media Engine.

---

# 11. Environment

Current environmental state.

Example

```json
{
    "weather":"Sunny",

    "temperature":"Warm",

    "time_of_day":"Morning",

    "noise":"Quiet"
}
```

Environment changes over time.

---

# 12. Connections

Defines traversable paths.

Example

```json
[
    "loc_library",

    "loc_corridor",

    "loc_entrance_hall"
]
```

Travel is only allowed through valid connections.

---

# 13. Occupants

Current entities inside the location.

Example

```json
[
    "char_harry",

    "char_hermione",

    "char_draco"
]
```

Generated dynamically.

Never stored permanently by Universe Builder.

---

# 14. Objects

Objects currently present.

Example

```json
[
    "obj_sorting_hat",

    "obj_house_cup"
]
```

Objects reference locations.

Locations reference objects.

---

# 15. Active Events

Current events occurring.

Example

```json
[
    "evt_breakfast",

    "evt_sorting"
]
```

Simulation Engine updates this list.

---

# 16. Local Rules

Some locations override global behavior.

Example

```text
Forbidden Forest

↓

Magic creatures may attack.
```

or

```text
Gringotts Vault

↓

Only goblins may access vaults.
```

Rules are references.

Not duplicated.

---

# 17. Visibility

Not every occupant is always visible.

Example

```json
{
    "visible":[
        "char_harry"
    ],

    "hidden":[
        "char_snape"
    ]
}
```

Useful for stealth mechanics.

---

# 18. Scene Construction

Every user interaction begins by constructing a scene.

```text
Current Location

↓

Occupants

↓

Objects

↓

Environment

↓

Events

↓

Narration
```

Example

```text
Great Hall

Morning sunlight spills across the enchanted ceiling.

Harry quietly eats breakfast.

Hermione reads beside him.

Owls occasionally fly overhead.
```

---

# 19. Character Movement

Movement updates

Current Location

↓

Old Occupants

↓

New Occupants

↓

World State

Example

```text
Harry

Library

↓

Great Hall
```

Library loses Harry.

Great Hall gains Harry.

---

# 20. Object Movement

Objects move similarly.

Example

```text
Book

Library Shelf

↓

Hermione Inventory
```

Location updates automatically.

---

# 21. Travel Validation

Travel Engine verifies

✔ Connection exists

✔ Route allowed

✔ User has permission

✔ Rules satisfied

Otherwise

Reject travel.

---

# 22. Location Discovery

Some locations begin hidden.

Example

```text
Room of Requirement

Visible?

False
```

Discovery updates visibility.

---

# 23. World State Updates

The following are mutable:

Occupants

Objects

Environment

Events

Weather

Lighting

Time

The following are immutable:

Name

Architecture

Description

Connections

Category

---

# 24. Navigation Graph

Locations form a graph.

Example

```text
Great Hall

│

├── Library

├── Corridor

├── Entrance Hall

└── Kitchens
```

No location should be isolated unless intentionally.

---

# 25. Interaction Context

When generating dialogue,

the Character Engine also receives location context.

Example

```json
{
    "location":"Great Hall",

    "weather":"Sunny",

    "time":"Morning",

    "occupants":[
        "Harry",
        "Hermione"
    ],

    "active_events":[
        "Breakfast"
    ]
}
```

This grounds conversations.

---

# 26. Validation Rules

Every location must satisfy:

✔ Unique ID

✔ Name exists

✔ Category exists

✔ Valid parent location (if present)

✔ Valid connected locations

✔ Valid object references

✔ Valid occupant references

✔ Valid event references

✔ No duplicate IDs

Reject invalid locations.

---

# 27. Storage

Locations are stored independently.

```text
universes/

    hp_001/

        locations/

            great_hall.json

            library.json

            forbidden_forest.json

            common_room.json
```

Only modified locations require saving.

---

# 28. Engine Responsibilities

Universe Builder

* Extract locations
* Build navigation graph
* Generate canonical descriptions

Interaction Engine

* Build scene

Simulation Engine

* Update occupants
* Update environment
* Trigger events
* Handle movement

Media Engine

* Read appearance
* Generate illustrations

Storage Engine

* Persist location state

---

# 29. Future Extensions

The schema supports additional systems such as:

```text
Dynamic lighting

Seasonal changes

NPC schedules

Random encounters

Weather simulation

Soundscape metadata

Ambient effects

Location reputation

Fog of war

Fast travel

Mini maps
```

These can be layered onto the existing model without altering the core location schema.

---

# 30. Summary

Locations are **persistent world entities**, not static backgrounds.

They provide the spatial foundation of the universe, defining where characters, objects, and events exist. While their canonical structure remains faithful to the original story, their contents evolve continuously through simulation, enabling users to explore a living world where every scene reflects the current state of the universe rather than a scripted moment from the source material.
