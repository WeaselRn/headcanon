# Indexes

## Purpose

The Index System enables efficient lookup of entities within a universe without scanning the complete World State.

Indexes improve the performance of search, navigation, simulation, and interaction by maintaining optimized references to frequently accessed data.

Indexes are derived data structures and should never become the source of truth.

The World State remains authoritative.

---

# Responsibilities

The Index System is responsible for

- Fast entity lookup
- Scene generation
- Character retrieval
- Object retrieval
- Timeline lookup
- Snapshot discovery
- Media lookup

---

# Index Categories

The system maintains indexes for

- Universes
- Characters
- Locations
- Objects
- Events
- Relationships
- Snapshots
- Generated Media

---

# Universe Index

Stores

- Universe ID
- Name
- Source Story
- Created Timestamp
- Last Modified
- Current Snapshot
- Status

Used for loading available universes.

---

# Character Index

Each character entry stores

- Character ID
- Name
- Current Location
- Current Scene
- Current Emotion
- Status

Allows instant retrieval without scanning all character records.

---

# Location Index

Each location stores

- Location ID
- Name
- Parent Location
- Connected Locations
- Current Occupants

Used for

- Scene generation
- Navigation
- Travel validation

---

# Object Index

Stores

- Object ID
- Name
- Category
- Current Owner
- Current Location
- Current Condition

Supports inventory operations and object interactions.

---

# Event Index

Stores

- Event ID
- Event Type
- Current Status
- Location
- Timestamp

Used by the Simulation Engine to evaluate pending and active events.

---

# Relationship Index

Stores relationships between

- Character ↔ Character
- Character ↔ Object
- Character ↔ Location
- Character ↔ Event

Optimized for fast graph traversal.

---

# Snapshot Index

Stores

- Snapshot ID
- Universe ID
- Save Type
- Timestamp
- Current Location
- Current Chapter

Allows efficient loading of saved sessions.

---

# Media Index

Stores references to

- Scene Images
- Character Portraits
- Narration Audio
- Ambient Audio

Each record contains

- Asset ID
- Universe ID
- Scene ID
- Asset Type
- Storage Path
- Metadata

Large media files remain stored in Backblaze B2.

---

# Index Updates

Indexes should be updated whenever

- A universe is created
- Characters move
- Objects change ownership
- Events change state
- Snapshots are created
- Media assets are generated

Updates should occur immediately after a successful World State update.

---

# Consistency

Indexes must always remain synchronized with the World State.

If an inconsistency is detected

↓

Rebuild the affected index

↓

Validate references

↓

Resume normal operation

Indexes should never contain orphaned or invalid references.

---

# Performance

Indexes should provide

- Constant-time lookup where practical
- Efficient filtering
- Fast search
- Minimal storage overhead

Indexes should improve performance without duplicating large amounts of data.

---

# Future Extensions

Potential improvements

- Full-text search
- Semantic search
- Knowledge graph indexing
- Vector embeddings
- Distributed indexing

---

# Related Documents

- 02_storage_schema.md
- 06_snapshots.md
- 07_cache.md
- ../universe/09_world_state.md
- ../engines/04_simulation_engine.md