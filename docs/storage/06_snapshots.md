# Snapshots

## Purpose

The Snapshot System preserves the complete runtime state of a universe at a specific point in time.

Snapshots allow users to safely pause, resume, restore, or branch their interactive universes without modifying the original reconstructed universe.

Unlike the Universe Model, snapshots represent the evolving state produced by simulation.

---

# Responsibilities

The Snapshot System is responsible for

- Saving World State
- Versioning progress
- Supporting restore
- Enabling rollback
- Preserving simulation continuity

---

# Snapshot Contents

A snapshot stores references to

- Universe ID
- World State
- Character States
- Relationship States
- Timeline State
- Active Events
- Pending Events
- Current Scene
- Metadata

Generated media is referenced rather than duplicated.

---

# Snapshot Types

Automatic

Created by the system after important interactions.

Manual

Created explicitly by the user.

Checkpoint

Created after major narrative milestones.

Recovery

Temporary snapshot before risky operations.

---

# Snapshot Lifecycle

Current World State

↓

Validation

↓

Serialization

↓

Compression (optional)

↓

Storage

↓

Metadata Update

---

# Restore Process

Load Snapshot

↓

Validate

↓

Restore World State

↓

Restore Timeline

↓

Restore Characters

↓

Generate Current Scene

↓

Resume Session

---

# Versioning

Every snapshot stores

- Snapshot Version
- Schema Version
- Engine Version
- Prompt Version

Snapshots should remain forward compatible whenever possible.

---

# Storage Strategy

Snapshots should contain only mutable runtime data.

Static universe information should always be referenced using the Universe ID.

This minimizes storage duplication.

---

# Validation

Before saving

Verify

- Valid Universe
- Valid World State
- Valid Timeline
- Existing Character References
- Existing Object References

Reject invalid snapshots.

---

# Recovery

If restoration fails

- Abort loading
- Preserve current session
- Attempt previous valid snapshot
- Report failure

The system must never partially restore a snapshot.

---

# Performance

Snapshot creation should

- Run asynchronously
- Minimize serialization time
- Avoid blocking gameplay
- Support incremental updates

---

# Future Extensions

Potential improvements

- Timeline branching
- Save thumbnails
- Snapshot comparison
- Differential snapshots
- Cloud synchronization

---

# Related Documents

- ../universe/15_snapshot_schema.md
- 02_storage_schema.md
- 05_versioning.md
- ../engines/04_simulation_engine.md