# Storage Schema

## Purpose

This document defines every persistent object stored by Headcanon.

The storage schema is the single source of truth for persistence.

Every backend service must serialize and deserialize data according to these schemas.

The storage schema is independent of

- Backblaze B2
- Local filesystem
- S3
- Databases

Changing storage providers must never require changing these schemas.

---

# Storage Objects

The persistent universe consists of the following objects.

```
Universe

↓

World State

↓

Timeline

↓

Character Memories

↓

Relationships

↓

Media

↓

Metadata

↓

Provenance

↓

Snapshots
```

---

# Universe

File

```
universe.json
```

Contains immutable information extracted from the source story.

Example

```json
{
  "id": "hp_001",
  "title": "Harry Potter",
  "source": "Harry Potter and the Philosopher's Stone",

  "characters": [],
  "locations": [],
  "objects": [],
  "rules": [],
  "knowledge_graph": []
}
```

The universe should never change after reconstruction.

---

# World State

File

```
world_state.json
```

Contains the current state of the simulation.

Example

```json
{
  "current_location": "Great Hall",

  "day": 3,

  "weather": "Sunny",

  "active_characters": [],

  "world_flags": [],

  "active_events": []
}
```

This file changes continuously.

---

# Character Memories

File

```
memories.json
```

Stores every character's memory.

Example

```json
{
  "Hermione": {
    "memories": [
      {
        "timestamp": "...",
        "summary": "...",
        "importance": 0.93
      }
    ]
  }
}
```

Memories are append-only.

Old memories are never deleted.

---

# Relationships

File

```
relationships.json
```

Example

```json
{
  "Harry": {
    "Hermione": 96,
    "Ron": 98,
    "User": 44
  }
}
```

Relationship values range

```
-100

↓

0

↓

100
```

---

# Timeline

File

```
timeline.json
```

Contains every event in chronological order.

Example

```json
{
  "events": [
    {
      "id": "evt001",
      "day": 1,
      "title": "...",
      "status": "completed"
    }
  ]
}
```

Possible statuses

- planned
- active
- completed
- cancelled
- altered

---

# Metadata

File

```
metadata.json
```

Contains descriptive information.

Example

```json
{
  "title": "...",
  "created_at": "...",
  "updated_at": "...",
  "engine_version": "...",
  "snapshot_count": 12
}
```

Metadata never stores simulation data.

---

# Provenance

File

```
provenance.json
```

Contains AI generation information.

Example

```json
{
  "pipeline_version": "...",
  "models": [],
  "generated_assets": [],
  "generation_time": "...",
  "storage_version": "1.0"
}
```

This is required for reproducibility.

---

# Media Index

File

```
media_index.json
```

Rather than scanning folders,

Headcanon maintains a complete media registry.

Example

```json
{
  "assets": [
    {
      "id": "...",
      "type": "image",
      "path": "...",
      "scene": "...",
      "created_at": "..."
    }
  ]
}
```

This allows fast retrieval.

---

# Snapshot

Each snapshot stores

```
snapshot/

    world_state.json

    timeline.json

    relationships.json

    memories.json

    metadata.json
```

Snapshots are immutable.

A snapshot represents the complete universe at one point in time.

---

# Save Frequency

The backend should save

- after every user interaction
- after every simulation update
- after media generation
- before shutdown
- after imports

No important state should exist only in memory.

---

# Versioning

Every JSON object contains

```json
{
  "schema_version": "1.0"
}
```

Future schema migrations should use this version.

---

# Atomic Saves

Multiple files must never be partially written.

Saving a universe should be treated as one transaction.

If one file fails,

the previous consistent version should remain intact.

---

# Storage Principles

Every stored object should satisfy

- deterministic
- human-readable
- versioned
- serializable
- recoverable
- portable

Storage must never depend on LLM output formatting.

Only validated application models may be written.