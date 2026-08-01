# Backblaze B2 Storage Architecture

## Purpose

Backblaze B2 is the persistent storage layer for Headcanon.

It stores every generated universe, every world snapshot, every media asset,
and every piece of provenance required to completely reconstruct a user's
interactive universe.

The storage layer must never contain business logic.

It is responsible only for:

- persistence
- retrieval
- versioning
- organization

Everything else belongs to the application layer.

---

# Goals

The storage layer should satisfy the following requirements.

## Persistence

Universes should never disappear unless explicitly deleted.

A user can return months later and continue exploring exactly where they left off.

---

## Scalability

Storage must support

- thousands of universes
- millions of generated assets
- multiple snapshots
- future multiplayer support

without changing directory structure.

---

## Determinism

The same universe ID always maps to the same storage prefix.

No random folder names.

---

## Immutable Assets

Generated assets should never be modified.

Instead,

create a new asset

update metadata

preserve provenance.

---

## Versioning

Every universe can have multiple snapshots.

Example

Universe

↓

Snapshot 1

↓

Snapshot 2

↓

Snapshot 3

Users may revisit any previous snapshot.

---

# Root Layout

The bucket root contains

```

universes/

```

Every universe receives its own folder.

Example

```

universes/
hp\_001/
lotr\_031/
starwars\_887/
