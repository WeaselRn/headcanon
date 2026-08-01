# Snapshot Schema

## Purpose

The Snapshot System enables users to pause and resume their interactive universe without losing progress.

A snapshot represents the complete mutable state of a universe at a specific point in time.

The immutable Universe Model is never duplicated; snapshots store only the dynamic World State and associated metadata.

---

# Responsibilities

The Snapshot System is responsible for

- Saving universe progress
- Restoring previous sessions
- Supporting version history
- Maintaining snapshot integrity
- Enabling rollback after failures

---

# Snapshot Principles

Snapshots should

- Represent a single point in time
- Be immutable once created
- Reference the original Universe Model
- Be lightweight
- Support future compatibility

---

# Snapshot Structure

Each snapshot contains

- Snapshot ID
- Universe ID
- World State Version
- Timestamp
- Save Type
- World State
- Timeline State
- Character States
- Relationship States
- Metadata

---

# Save Types

Supported snapshot types

### Automatic

Created by the system

Examples

- After important interactions
- After major events
- Before media generation

---

### Manual

Created by the user.

Allows returning to important moments.

---

### Checkpoint

Generated during significant story milestones.

Examples

- End of Chapter
- Boss Battle
- Major Canon Event

---

# Stored Data

Every snapshot stores

## Character States

- Location
- Emotion
- Current Goal
- Inventory
- Relationships
- Recent Memories

---

## World State

- Current Time
- Weather
- Active Scene
- Active Events
- Pending Events

---

## Timeline

- Completed Events
- Cancelled Events
- Generated Events

---

## Objects

Store

- Current Owner
- Current Location
- Current Condition

---

## Metadata

Each snapshot records

- Creation Time
- World State Version
- Engine Version
- Prompt Version
- Schema Version

Metadata supports future migrations.

---

# Snapshot Creation

Snapshot creation flow

Current World State

↓

Validation

↓

Serialization

↓

Compression (optional)

↓

Backblaze Storage

↓

Metadata Update

---

# Snapshot Loading

Loading flow

Snapshot

↓

Validation

↓

Restore World State

↓

Restore Character States

↓

Restore Timeline

↓

Generate Current Scene

↓

Resume Interaction

---

# Snapshot Validation

Every snapshot must verify

- Universe exists
- World State valid
- Timeline consistent
- Character references valid
- Object references valid
- Relationship references valid

Invalid snapshots should never be loaded.

---

# Version Compatibility

Every snapshot stores

- Schema Version
- Engine Version
- Prompt Version

If versions differ,

migration should occur before loading.

---

# Storage

Snapshots should store

World State

Metadata

Relationships

Timeline

References to generated media

Large assets such as images and audio remain stored separately in Backblaze B2.

---

# Retention

The system may

- Keep the latest automatic snapshots
- Retain all manual snapshots
- Remove obsolete temporary snapshots

Retention policies should be configurable.

---

# Recovery

If snapshot loading fails

- Keep the current universe unchanged
- Report the failure
- Attempt loading the previous valid snapshot

Snapshots must never corrupt the World State.

---

# Design Principles

The Snapshot System should

- Be deterministic
- Be versioned
- Be recoverable
- Minimize storage duplication
- Support long-running universes

---

# Related Documents

- 09_world_state.md
- 10_events.md
- ../storage/02_storage_schema.md
- ../storage/05_versioning.md
- ../engines/04_simulation_engine.md
- ../engines/10_media_pipeline.md