# Runtime Pipeline

## Purpose

## High-Level Pipeline

## Phase 1 — Story Import
- Input formats
- Validation
- Text extraction

## Phase 2 — Universe Reconstruction
- Entity extraction
- Character extraction
- Locations
- Timeline
- Relationships
- World rules

## Phase 3 — World Initialization
- Initial world state
- Character memories
- Inventories
- Scene graph
- Event queue

## Phase 4 — User Session
- Loading a universe
- Restoring state
- Entering first scene

## Phase 5 — Interaction Loop
1. User action
2. Action validation
3. Character reasoning
4. World simulation
5. State update
6. Scene regeneration
7. UI update

## Phase 6 — Persistence
- Autosave
- Snapshots
- Version history

## Phase 7 — Session Resume
- Loading snapshots
- Restoring memories
- Continuing simulation

## Pipeline Diagram

User Story
    ↓
Import
    ↓
Universe Builder
    ↓
World Initialization
    ↓
Interactive Simulation Loop
    ↓
Save Snapshot
    ↓
Resume Later

## Related Documents

- universe_builder.md
- simulation_engine.md
- storage.md
- frontend/navigation.md
- api/*.md