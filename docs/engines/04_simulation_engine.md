# `docs/engines/04_simulation_engine.md`

---

# Simulation Engine

**Version:** 1.0

**Status:** Draft

**Owner:** World Simulation System

---

# 1. Purpose

The Simulation Engine is the heart of Headcanon.

Every meaningful user action eventually reaches this engine.

Its responsibility is to answer one question:

> **"Given the current world state, what changes?"**

Unlike the Character Engine, which determines what a character says, the Simulation Engine determines what actually happens.

It is responsible for ensuring that the universe evolves logically while remaining faithful to its canonical rules.

---

# 2. Responsibilities

The Simulation Engine is responsible for:

* Executing validated actions
* Updating the World State
* Simulating consequences
* Progressing time
* Triggering events
* Moving characters
* Moving objects
* Updating goals
* Updating relationships
* Creating world mutations
* Requesting timeline updates

It is **not responsible** for:

* Dialogue generation
* Media generation
* Scene narration
* Parsing user intent

---

# 3. Inputs

The Simulation Engine receives:

```text
Validated Interaction

↓

Current World State

↓

Universe

↓

Current Timeline

↓

Active Rules
```

Example

```text
User

↓

Give Elder Wand to Hermione
```

---

# 4. Outputs

The engine produces a World Mutation.

Example

```json
{
    "changes":[
        "Ownership changed",
        "Relationship increased",
        "Harry observed interaction"
    ],

    "timeline_updates":[...],

    "new_events":[...],

    "scene_refresh":true
}
```

The Simulation Engine never produces dialogue.

---

# 5. High-Level Pipeline

```text
Validated Action

↓

Load World State

↓

Validate Rules

↓

Predict Consequences

↓

Execute Changes

↓

Update Timeline

↓

Generate World Mutations

↓

Save Snapshot
```

---

# 6. Internal Architecture

```text
Simulation Engine

├── Rule Validator

├── Action Executor

├── Consequence Generator

├── Timeline Updater

├── Character Updater

├── Object Updater

├── Event Manager

├── Snapshot Builder

└── Validator
```

---

# 7. Rule Validation

Before executing anything,

verify

✔ Canon rules

✔ World rules

✔ Character abilities

✔ Object constraints

✔ Environmental constraints

Example

```text
User

↓

Fly

↓

No broom

↓

Reject
```

---

# 8. Action Execution

Examples

```text
Take Object

↓

Inventory Update

↓

Location Update
```

or

```text
Travel

↓

Location Update

↓

Occupant Update

↓

Scene Refresh
```

---

# 9. Consequence Generation

Every action has direct and indirect consequences.

Example

```text
User

↓

Steals Wand

↓

Owner loses wand

↓

Trust decreases

↓

Nearby witnesses react

↓

Future events change
```

Simulation must propagate consequences.

---

# 10. World Mutation

Everything is represented as mutations.

Example

```json
{
    "entity":"char_harry",

    "field":"location",

    "old":"Library",

    "new":"Great Hall"
}
```

Mutations are atomic.

---

# 11. Time Progression

Some actions advance time.

Example

```text
Wait

↓

+30 Minutes
```

or

```text
Travel

↓

+10 Minutes
```

Time progression may trigger scheduled events.

---

# 12. Event Triggering

Example

```text
Current Time

↓

8:00 AM

↓

Breakfast Begins
```

↓

Generate Event

↓

Update Scene

Events are deterministic.

---

# 13. Character Updates

Simulation updates

* location
* goals
* emotional state
* activities
* inventories

Example

```text
Hermione

↓

Library

↓

Great Hall
```

---

# 14. Object Updates

Example

```text
Book

↓

Shelf

↓

User Inventory
```

All references remain synchronized.

---

# 15. Relationship Effects

Actions influence relationships.

Example

```text
Help Hermione

↓

+8 Trust

↓

+3 Friendship
```

Negative actions decrease affinity.

---

# 16. Knowledge Propagation

Information spreads.

Example

```text
User defeats troll.

↓

Harry sees event.

↓

Harry knows.

↓

Ron hears later.

↓

Ron partially knows.
```

Knowledge does not magically appear.

---

# 17. Goal Updates

Characters adapt.

Example

Hermione

Goal

```text
Study
```

↓

Troll appears

↓

Goal becomes

```text
Escape
```

Goals change dynamically.

---

# 18. Chain Reactions

One action may create multiple effects.

Example

```text
User

↓

Convince Ron to Leave

↓

Ron Leaves

↓

Harry Lonely

↓

Hermione Talks More

↓

Future Quidditch Match Changes

↓

Timeline Diverges
```

This is what makes the world feel alive.

---

# 19. Timeline Requests

Simulation never edits the timeline directly.

Instead

```text
Simulation

↓

Timeline Engine

↓

Append Timeline Mutation
```

---

# 20. Snapshot Creation

Every successful mutation creates a snapshot.

```text
Snapshot

↓

World State

↓

Timestamp

↓

Reason

↓

Mutation List
```

Snapshots enable persistence.

---

# 21. Validation

Validator checks

✔ Valid mutations

✔ Valid references

✔ No duplicate ownership

✔ Characters exist

✔ Locations exist

✔ Objects exist

✔ Rules preserved

Reject inconsistent states.

---

# 22. Prompt Strategy

Simulation should use specialized prompts.

```text
simulate_action.txt

predict_consequences.txt

update_world_state.txt

propagate_effects.txt

validate_simulation.txt
```

Never use one monolithic prompt.

---

# 23. Engine Communication

Reads

```text
Universe

World State

Timeline

Rules

Characters

Objects
```

Calls

```text
Timeline Engine

Relationship Engine

Memory Engine

Scene Engine
```

Updates

```text
World State

Snapshots
```

---

# 24. Performance Considerations

The Simulation Engine should only update affected entities.

Example

User speaks to Hermione.

Do **not** recompute

* every relationship
* every NPC
* every location

Only recompute impacted entities.

This keeps simulation scalable for very large universes.

---

# 25. Future Extensions

The engine supports future systems including

```text
Daily schedules

Weather simulation

Economy

Politics

Faction wars

Creature AI

Quest system

Crafting

Combat

Random encounters

Disease

Aging
```

These systems plug into the mutation pipeline.

---

# 26. Example End-to-End Flow

```text
User

↓

Take Marauder's Map

↓

Validate

↓

Move Object

↓

Update Inventory

↓

Harry Notices

↓

Trust -5

↓

Hermione Learns Later

↓

Relationship Update

↓

Timeline Event

↓

Snapshot Saved

↓

Scene Refresh
```

---

# 27. Summary

The Simulation Engine is the **physics engine** of Headcanon.

It ensures that every action has believable consequences, every world mutation obeys canonical rules, and every change is propagated consistently across characters, objects, locations, relationships, and future events. Rather than scripting outcomes, it evolves the universe through deterministic world mutations, making each user's playthrough a unique but internally consistent version of the original story.
