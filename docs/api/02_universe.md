# Universe API

## Purpose

The Universe API manages existing universes after they have been imported.

It provides endpoints for retrieving universe information, loading world state, updating metadata, listing universes, and deleting universes.

This API does not perform simulation. It manages universe lifecycle and persistence.

---

# Responsibilities

The Universe API is responsible for

- Retrieving universes
- Listing available universes
- Loading World State
- Returning universe metadata
- Deleting universes
- Updating universe metadata

---

# Endpoint

GET

/api/v1/universes

Returns all available universes.

---

# Endpoint

GET

/api/v1/universes/{universe_id}

Returns

- Universe Metadata
- Current World State Version
- Current Snapshot
- Creation Date
- Last Modified

---

# Endpoint

PATCH

/api/v1/universes/{universe_id}

Updates editable metadata.

Supported fields

- Name
- Description
- Tags
- Favorite

The Universe Model itself is immutable.

---

# Endpoint

DELETE

/api/v1/universes/{universe_id}

Deletes

- Universe
- World State
- Snapshots
- Generated Media
- Metadata

Deletion is permanent.

Future versions may support soft deletion.

---

# Endpoint

GET

/api/v1/universes/{universe_id}/metadata

Returns

- Story Title
- Source Type
- Imported Date
- Universe Version
- Engine Version
- Prompt Version
- Current Snapshot

---

# Endpoint

GET

/api/v1/universes/{universe_id}/status

Returns runtime information.

Example

{
    "status": "active",
    "world_state_version": 18,
    "current_scene": "scene_042",
    "autosave": true
}

---

# Validation

Before every request

Verify

- Universe exists
- Universe ID valid
- User has access (future)

Invalid universes return

404 Not Found

---

# Successful Response

Typical response

{
    "universe_id": "...",
    "name": "...",
    "created_at": "...",
    "last_modified": "...",
    "world_state_version": 18,
    "current_snapshot": "...",
    "status": "active"
}

---

# Error Responses

400

Bad Request

404

Universe Not Found

409

Universe Locked

500

Internal Server Error

---

# Lifecycle

Import Story

↓

Universe Created

↓

World Initialized

↓

Interactions

↓

Snapshots

↓

Media Generation

↓

Deletion (optional)

---

# Performance

Universe metadata should load quickly.

Large assets

- Images
- Narration
- Snapshots

should be loaded lazily when required.

---

# Security

Never expose

- Internal prompt files
- Storage credentials
- API keys
- Internal engine state

Validate every Universe ID before processing.

---

# Future Extensions

Potential additions

- Universe duplication
- Universe export
- Universe sharing
- Collaboration
- Public universes
- Archive / Restore

---

# Related Documents

- ../universe/09_world_state.md
- ../storage/02_storage_schema.md
- ../storage/06_snapshots.md
- ../runtime_pipeline.md