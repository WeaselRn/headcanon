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

---

# Runtime Interaction Pipeline

Every user interaction follows the same execution pipeline.

```
User Action
      │
      ▼
Interaction Engine
      │
      ▼
Character Engine
      │
      ▼
Memory Engine
      │
      ▼
Relationship Engine
      │
      ▼
Simulation Engine
      │
      ▼
Timeline Engine
      │
      ▼
Persist World State
      │
      ▼
Scene Engine
      │
      ▼
(Optional)
Media Pipeline
      │
      ▼
Frontend Response
```

The execution order is fixed.

No engine may skip or reorder another engine unless explicitly documented.

---

# Engine Execution Responsibilities

## Interaction Engine

- Parse user action.
- Identify target entities.
- Validate action.
- Produce interaction context.

Output

```
InteractionContext
```

---

## Character Engine

- Generate in-character response.
- Respect personality.
- Respect memories.
- Respect world rules.

Output

```
CharacterResponse
```

---

## Memory Engine

- Determine if interaction should become memory.
- Store new memories.
- Update existing memories.

Output

```
MemoryChanges
```

---

## Relationship Engine

- Update affinity.
- Update trust.
- Update fear.
- Update respect.

Output

```
RelationshipChanges
```

---

## Simulation Engine

- Execute world consequences.
- Move NPCs.
- Update inventories.
- Trigger events.
- Apply world mutations.

Output

```
WorldStateDelta
```

---

## Timeline Engine

- Advance time.
- Complete events.
- Schedule future events.
- Record important events.

Output

```
TimelineDelta
```

---

## Scene Engine

- Build updated scene.
- Determine visible entities.
- Generate narration.
- Generate available actions.

Output

```
Scene
```

---

## Media Pipeline

Runs only when requested.

Responsible for

- Scene illustration
- Narration audio
- Ambient audio
- Metadata
- Backblaze upload

---

# Persistence Pipeline

After every successful interaction

```
WorldState

↓

Validate

↓

Save

↓

Update Snapshot

↓

Return Response
```

Universe data is never modified.

Only World State is persisted.

---

# Failure Handling

If an engine fails

```
Stop Pipeline

↓

Rollback World State

↓

Return Error

↓

Do Not Persist
```

Partial updates are never committed.

---

# Pipeline Guarantees

The runtime pipeline guarantees

- Deterministic execution order.
- Canonical universe remains immutable.
- Only World State is mutated.
- Every mutation is persisted.
- Every response reflects the latest World State.
- Every engine has a single responsibility.
- Engine outputs become inputs for the next engine.