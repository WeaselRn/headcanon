# Versioning

## Purpose

Headcanon is a persistent universe simulation.

Unlike traditional save systems, the universe continuously evolves through
interactions, simulations, and generated media.

The Versioning system ensures that every change is safely recorded while
allowing previous states to be revisited or restored.

Versioning applies to the universe state, not individual media assets.

---

# Goals

The Versioning system should provide

- safe persistence
- historical replay
- rollback
- branching support
- deterministic saves
- migration compatibility

---

# Version Hierarchy

The version hierarchy is

```
Universe

↓

Branch

↓

Snapshot

↓

Revision
```

Each level has a different responsibility.

---

# Universe

A universe represents one imported story.

Example

```
Harry Potter

↓

Universe ID

hp_001
```

There is exactly one root universe.

---

# Branch

A branch represents one timeline.

Example

```
Original Canon

↓

Branch A

↓

Branch B
```

Future feature:

Users may create alternate timelines without destroying previous ones.

---

# Snapshot

Snapshots capture the complete world state.

Example

```
Snapshot 001

↓

Snapshot 002

↓

Snapshot 003
```

Every snapshot represents a playable universe.

---

# Revision

Revisions are internal save operations.

Example

```
Snapshot 24

↓

Revision 1

↓

Revision 2

↓

Revision 3
```

Normally users never see revisions.

They exist for

- autosave
- crash recovery
- synchronization

---

# Snapshot Creation

Create a snapshot after

- story import
- important interaction
- simulation update
- media generation
- explicit user save

Minor operations may create revisions instead.

---

# Immutable Snapshots

Snapshots are immutable.

Never modify an existing snapshot.

Instead

```
Snapshot 8

↓

Create Snapshot 9
```

---

# Active Snapshot

Each universe maintains

```
active_snapshot
```

Example

```json
{
    "active_snapshot": "snapshot_0018"
}
```

Loading a universe loads this snapshot.

---

# Snapshot Metadata

Each snapshot stores

```json
{
    "snapshot_id": "snapshot_0018",

    "created_at": "...",

    "parent_snapshot": "snapshot_0017",

    "branch": "main",

    "reason": "interaction",

    "description": "User convinced Ron to stay."
}
```

---

# Parent Relationship

Every snapshot references its parent.

Example

```
1

↓

2

↓

3

↓

4
```

This creates a complete history.

---

# Future Branches

Branching enables alternate universes.

Example

```
Snapshot 18

↓

Branch A

↓

19

↓

20


Snapshot 18

↓

Branch B

↓

19

↓

20
```

Branches share the same origin.

---

# Rollback

Rollback should

- change the active snapshot
- preserve newer snapshots
- never delete history

Rollback is reversible.

---

# Migration

Every snapshot contains

```json
{
    "schema_version": "1.0",

    "engine_version": "2.0"
}
```

Future migrations use these fields.

---

# Compatibility

Older universes should continue working after upgrades.

Migration scripts should convert

```
1.0

↓

1.1

↓

2.0
```

without data loss.

---

# Save Strategy

Saving should follow

```
World Update

↓

Validation

↓

Snapshot Creation

↓

Storage

↓

Metadata Update

↓

Activate Snapshot
```

Never activate an incomplete snapshot.

---

# Failure Recovery

If saving fails

- previous snapshot remains active
- partial files are discarded
- recovery logs are written

The universe must never become corrupted.

---

# Version IDs

Snapshot IDs

```
snapshot_000001
```

Branch IDs

```
main

alternate_001

user_branch_001
```

Revision IDs

```
rev_000001
```

Deterministic IDs simplify debugging.

---

# Future Features

The versioning system should support

- multiplayer synchronization
- cloud synchronization
- collaborative universes
- timeline branching
- merge operations
- selective rollback

without changing the storage model.

---

# Design Principles

Versioning must be

- deterministic
- append-only
- immutable
- recoverable
- scalable

Every playable state of a universe should always be reproducible.