# `docs/engines/08_timeline_engine.md`

---

# Timeline Engine

**Version:** 1.0

**Status:** Draft

**Owner:** Timeline & Continuity System

---

# 1. Purpose

The Timeline Engine is responsible for maintaining the chronological history of the universe.

Unlike the Memory Engine (which stores what characters remember), the Timeline Engine stores **what objectively happened**.

It ensures that the universe remains internally consistent as users alter events, create new ones, or diverge from the original story.

It answers:

> **"Given everything that has happened so far, what is now the history of this universe?"**

---

# 2. Design Philosophy

The Timeline should be:

* chronological
* immutable in history
* append-only
* explainable
* replayable
* branch-aware

Nothing is ever silently overwritten.

---

# 3. Responsibilities

The Timeline Engine is responsible for:

* Recording new events
* Updating event status
* Tracking canonical divergence
* Maintaining event ordering
* Creating timeline branches
* Resolving event dependencies
* Supporting replay
* Providing timeline context

It is **not responsible** for:

* Dialogue
* Character memories
* Relationship updates
* World simulation

---

# 4. Inputs

```text
Simulation Engine

↓

World Mutations

↓

Current Timeline

↓

Current World State
```

---

# 5. Outputs

Example

```json
{
    "new_events":[...],

    "modified_events":[...],

    "timeline_branch":"branch_001",

    "continuity_status":"diverged"
}
```

---

# 6. High-Level Pipeline

```text
World Mutation

↓

Determine Timeline Effect

↓

Create Event

↓

Check Dependencies

↓

Update Timeline

↓

Detect Divergence

↓

Persist Timeline
```

---

# 7. Internal Architecture

```text
Timeline Engine

├── Event Creator

├── Event Validator

├── Dependency Resolver

├── Branch Manager

├── Continuity Checker

├── Timeline Builder

├── Snapshot Recorder

└── Validator
```

---

# 8. Timeline Schema

```json
{
    "timeline_id":"main",

    "events":[],

    "branches":[],

    "current_time":"",

    "current_day":0,

    "divergence_points":[]
}
```

---

# 9. Event Schema

```json
{
    "id":"evt_001",

    "title":"Sorting Ceremony",

    "timestamp":"",

    "participants":[],

    "location":"",

    "status":"completed",

    "canonical":true,

    "parent_events":[],

    "consequences":[],

    "metadata":{}
}
```

---

# 10. Event Types

Supported types

```text
Story Event

Interaction

Combat

Conversation

Travel

Discovery

Relationship

Quest

Object Change

Environmental

World Event
```

---

# 11. Canonical Events

Canonical events originate from the source story.

Example

```text
Harry receives Hogwarts letter.
```

Stored as

```json
{
    "canonical":true
}
```

---

# 12. Generated Events

User-created events are marked separately.

Example

```text
User teaches Hermione programming.
```

↓

```json
{
    "canonical":false
}
```

---

# 13. Event Dependencies

Some events depend on others.

Example

```text
Receive Hogwarts Letter

↓

Travel to Hogwarts

↓

Sorting Ceremony
```

Dependencies prevent impossible timelines.

---

# 14. Divergence Detection

Example

Canon

```text
Ron becomes Harry's best friend.
```

User

```text
Convince Ron to leave Hogwarts.
```

↓

Timeline detects

```text
Canon Broken
```

↓

Create divergence point.

---

# 15. Timeline Branches

Timeline supports branching.

```text
Main Timeline

│

├── Canon

│

└── User Timeline
```

The original canon is preserved.

---

# 16. Branch Schema

```json
{
    "branch_id":"branch_001",

    "parent":"main",

    "created_after":"evt_023",

    "reason":"Ron leaves Hogwarts."
}
```

---

# 17. Event Ordering

Events are always ordered by

```text
Time

↓

Dependencies

↓

Creation Order
```

Never by insertion order alone.

---

# 18. Current Time

Timeline stores

```json
{
    "day":12,

    "time":"08:45",

    "season":"Autumn"
}
```

Time advances through Simulation Engine.

---

# 19. Consequences

Every event references its consequences.

Example

```text
Destroy Horcrux

↓

Voldemort Weakens

↓

Battle Easier
```

This enables causal reasoning.

---

# 20. Timeline Queries

The engine should support

```text
Recent Events

Events by Character

Events by Location

Events by Object

Canonical Events

Generated Events

Future Scheduled Events
```

---

# 21. Replay

The Timeline supports replay.

Example

```text
Show me everything that happened yesterday.
```

↓

Replay all events from that day.

---

# 22. Prompt Strategy

Timeline Engine uses

```text
create_event.txt

detect_divergence.txt

update_timeline.txt

resolve_dependencies.txt

validate_timeline.txt
```

Each prompt performs one responsibility.

---

# 23. Validation

Validator checks

✔ Valid timestamps

✔ Valid participants

✔ Valid locations

✔ Valid dependencies

✔ No circular references

✔ Chronological consistency

Reject invalid timelines.

---

# 24. Engine Communication

Reads

```text
World State

Simulation Results

Characters

Locations

Objects
```

Updates

```text
Timeline

Timeline Branches

Snapshots
```

Provides

```text
Timeline Context
```

to the Character and Simulation Engines.

---

# 25. Storage

```text
universes/

    hp_001/

        timeline/

            main.json

            branch_001.json

            snapshots/
```

Each branch is stored independently.

---

# 26. Performance Considerations

The Timeline Engine should:

* append events rather than rewrite history
* index events by time, location, and participants
* cache recent events
* load only relevant timeline windows for context

This keeps long-running universes performant.

---

# 27. Future Extensions

The Timeline Engine supports future systems including

```text
Alternate endings

Multiple save slots

Time travel

Parallel universes

Quest timelines

Historical analytics

Timeline visualization

Replay mode

Undo checkpoints
```

without changing the core event model.

---

# 28. Example End-to-End Flow

```text
User

↓

Saves Cedric Diggory

↓

Simulation Engine

↓

Cedric Survives

↓

Timeline Engine

↓

Detect Canon Divergence

↓

Create Branch

↓

Append Event

↓

Update Future Event Dependencies

↓

Persist Timeline
```

---

# 29. Timeline vs Memory

| Timeline          | Memory                      |
| ----------------- | --------------------------- |
| Objective         | Subjective                  |
| Global            | Per Character               |
| Never forgotten   | Can decay                   |
| Stores all events | Stores relevant experiences |
| Shared truth      | Individual perception       |

This distinction is fundamental to Headcanon's architecture.

---

# 30. Summary

The Timeline Engine is the **historian** of Headcanon.

It records the objective sequence of events that define the evolving universe, preserving both the original canon and every divergence created by the user. By tracking dependencies, maintaining chronological consistency, and supporting timeline branching, it ensures that every action has a traceable history and every alternate reality remains internally coherent. Together with the Simulation Engine, it transforms Headcanon from a conversational experience into a persistent, living world with its own evolving history.
