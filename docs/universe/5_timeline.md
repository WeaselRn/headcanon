# `docs/universe/05_timeline.md`

---

# Timeline

**Version:** 1.0

**Status:** Draft

**Owner:** Simulation Engine

---

# 1. Purpose

The Timeline records the chronological evolution of the universe.

Unlike the original story, the timeline is **not fixed**.

It begins with canon, but evolves as users interact with the world.

The Timeline is what allows Headcanon to answer questions like:

* "What happened yesterday?"
* "Has Ron already left Hogwarts?"
* "Who currently owns the Elder Wand?"
* "What changed because of my decision?"

The Timeline is the **memory of the world itself**.

---

# 2. Design Philosophy

The Timeline follows six core principles.

## Chronological

Every event has an order.

---

## Persistent

Events are never deleted.

---

## Branchable

Canon and user-created events coexist.

---

## Causal

Events produce consequences.

---

## Replayable

Any point in history can be reconstructed.

---

## Traceable

Every event records why it happened.

---

# 3. Timeline Lifecycle

```text
Story Import

↓

Universe Builder

↓

Extract Canon Events

↓

Build Initial Timeline

↓

User Action

↓

Simulation

↓

Generate New Event

↓

Update Timeline

↓

Save Snapshot
```

---

# 4. Timeline Object

```json
{
  "current_time": {},
  "events": [],
  "active_events": [],
  "scheduled_events": [],
  "completed_events": [],
  "cancelled_events": [],
  "branches": [],
  "metadata": {}
}
```

---

# 5. Event Object

Every timeline entry follows the same schema.

```json
{
  "id": "",
  "title": "",
  "description": "",
  "type": "",
  "timestamp": "",
  "participants": [],
  "location": "",
  "status": "",
  "importance": 0,
  "causes": [],
  "consequences": [],
  "metadata": {}
}
```

---

# 6. Event Types

Supported event categories

```text
Story Event

Conversation

Combat

Travel

Discovery

Relationship Change

Item Transfer

Death

Quest

Environmental

World Event

User Action

Simulation
```

New types can be added.

---

# 7. Canon Events

Universe Builder extracts canonical events.

Example

```text
Harry receives Hogwarts letter

↓

Sorting Ceremony

↓

First Potions Class

↓

Troll Attack
```

These become the initial timeline.

---

# 8. Generated Events

Simulation Engine creates new events.

Example

```text
User convinces Ron to quit Hogwarts.
```

This event never existed in canon.

---

# 9. Event Status

Each event has one status.

```text
Scheduled

Active

Completed

Cancelled

Failed
```

---

# 10. Event Importance

Importance determines permanence.

Scale

```text
0–20

Minor

21–50

Normal

51–80

Important

81–100

Critical
```

Critical events should never be removed.

---

# 11. Participants

Events reference IDs.

Example

```json
[
    "char_user",
    "char_harry",
    "char_ron"
]
```

Never store names.

---

# 12. Event Location

Example

```json
{
    "location":"loc_great_hall"
}
```

Enables location history.

---

# 13. Causes

Every event records its causes.

Example

```text
User insults Draco

↓

Draco challenges user

↓

Duel begins
```

Stored as

```json
[
    "evt_user_insult"
]
```

---

# 14. Consequences

Simulation produces consequences.

Example

```text
Ron leaves Hogwarts

↓

Harry becomes lonely

↓

Hermione spends more time with Harry

↓

Relationship updates

↓

Future events change
```

---

# 15. Active Events

Not every event is finished.

Example

```text
House Cup Competition

Status

Active
```

Simulation checks active events every world update.

---

# 16. Scheduled Events

Future events.

Example

```text
Quidditch Match

Tomorrow

2 PM
```

They automatically activate.

---

# 17. Cancelled Events

Example

```text
Canon

Harry meets Ron

↓

User prevents meeting

↓

Event

Cancelled
```

Cancelled events remain in history.

---

# 18. Branches

Timeline supports alternate history.

Example

```text
Canon

↓

Harry meets Ron

↓

Branch

Ron leaves Hogwarts

↓

New Timeline
```

Canon remains preserved.

---

# 19. Time Model

Time should be abstract.

Instead of

```text
14 August 1991
```

Use

```text
Day 14

Morning
```

or

```json
{
    "day":14,

    "hour":9
}
```

Works for every universe.

---

# 20. Time Progression

Time advances through

```text
Travel

Sleep

Waiting

Major Events

Simulation
```

Not every conversation advances time.

---

# 21. Event Generation

Simulation Engine creates

```text
User Action

↓

Simulation

↓

Determine Consequences

↓

Generate Timeline Event

↓

Update World State
```

Timeline is never manually edited.

---

# 22. Timeline Queries

Timeline supports

```text
Recent Events

Upcoming Events

Events by Character

Events by Location

Events by Object

Critical Events

Cancelled Events

User-created Events
```

---

# 23. Replay

Timeline enables replay.

Example

```text
Show me

The Battle of Hogwarts
```

Scene Engine reconstructs

* characters
* locations
* objects
* dialogue context

from that point.

---

# 24. Relationship with World State

Timeline stores history.

World State stores present.

Example

```text
Timeline

Harry gave wand to Hermione.

↓

World State

Owner

Hermione
```

Never duplicate current state inside Timeline.

---

# 25. Timeline Validation

Every event must satisfy

✔ Unique ID

✔ Valid timestamp

✔ Valid participants

✔ Valid location

✔ Valid causes

✔ Valid consequences

✔ Valid status

✔ Valid type

Reject invalid events.

---

# 26. Storage

```text
universes/

    hp_001/

        timeline/

            timeline.json

            events/

                evt_001.json

                evt_002.json

                evt_003.json
```

Large universes may store events separately.

---

# 27. Engine Responsibilities

Universe Builder

* Extract canon events
* Order chronology

Simulation Engine

* Generate events
* Cancel events
* Schedule events
* Advance time

Character Engine

* Read recent events
* Build memories

Interaction Engine

* Trigger new events

Storage Engine

* Save timeline snapshots

---

# 28. Future Extensions

Future systems

```text
Multiple timelines

Timeline merging

Parallel universes

Prophecy system

Time travel

Historical replay

Quest chains

Dynamic calendars

Seasonal events

Event prediction
```

These should extend the timeline without changing its core schema.

---

# 29. Example

Initial Timeline

```text
Day 1

Harry receives letter.

↓

Day 2

Visits Diagon Alley.

↓

Day 10

Sorting Ceremony.
```

User Interaction

```text
Convince Ron to stay home.
```

Generated Timeline

```text
Day 11

User convinces Ron not to board Hogwarts Express.

↓

Day 12

Harry arrives alone.

↓

Day 15

Hermione befriends Harry earlier.

↓

Day 20

Troll attack unfolds differently.
```

The original story remains visible as canon, while the active universe follows the new sequence of events.

---

# 30. Summary

The Timeline is **the historical backbone of the universe**.

It records every canonical and simulated event, preserves causality, and enables the world to evolve logically over time. By separating historical events from the current World State, Headcanon can support persistent memories, alternate timelines, event replay, and meaningful consequences without ever losing the original canon. This makes the universe feel alive, consistent, and continuously shaped by the user's actions.
