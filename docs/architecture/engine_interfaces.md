---

# Public Engine Interfaces

Each engine exposes exactly one public interface.

Other engines may only communicate through these interfaces.

Direct access to another engine's internal methods is prohibited.

---

# Universe Builder

## Purpose

Construct the canonical Universe from imported story text.

## Public Interface

```
build_universe(story_text) -> Universe
```

## Input

- Clean story text

## Output

- Universe

## Dependencies

- Import Service
- Universe Prompts
- Validator

## Never Calls

- Character Engine
- Simulation Engine
- Scene Engine

---

# Character Engine

## Purpose

Generate canon-consistent character responses.

## Public Interface

```
respond(context) -> CharacterResponse
```

## Input

- Character Context
- World State
- User Action

## Output

```
CharacterResponse
```

## Dependencies

- Universe
- World State

## Never Calls

- Timeline Engine
- Simulation Engine

---

# Memory Engine

## Purpose

Store and retrieve memories.

## Public Interface

```
update(world_state, interaction) -> MemoryChanges
```

## Input

- World State
- Character Response
- User Interaction

## Output

```
MemoryChanges
```

## Dependencies

- World State

## Never Calls

- Scene Engine
- Timeline Engine

---

# Relationship Engine

## Purpose

Update relationships between entities.

## Public Interface

```
update(world_state, interaction) -> RelationshipChanges
```

## Input

- World State
- Interaction

## Output

```
RelationshipChanges
```

## Dependencies

- World State

## Never Calls

- Character Engine
- Scene Engine

---

# Simulation Engine

## Purpose

Apply consequences of user actions.

## Public Interface

```
simulate(world_state, interaction) -> WorldStateDelta
```

## Input

- World State
- User Action
- Character Response

## Output

```
WorldStateDelta
```

## Dependencies

- Universe
- World State

## Never Calls

- Character Engine

---

# Timeline Engine

## Purpose

Advance the world's timeline.

## Public Interface

```
advance(world_state) -> TimelineDelta
```

## Input

- World State
- WorldStateDelta

## Output

```
TimelineDelta
```

## Dependencies

- World State

## Never Calls

- Character Engine
- Memory Engine

---

# Scene Engine

## Purpose

Generate the current playable scene.

## Public Interface

```
build_scene(world_state) -> Scene
```

## Input

- World State
- Universe

## Output

```
Scene
```

## Dependencies

- Universe
- World State

## Never Calls

- Simulation Engine

---

# Narration Engine

## Purpose

Generate narration for the current scene.

## Public Interface

```
generate(scene) -> Narration
```

## Input

- Scene

## Output

```
Narration
```

---

# Media Pipeline

## Purpose

Generate multimedia assets.

## Public Interface

```
generate(scene) -> MediaAssets
```

## Input

- Scene

## Output

- Images
- Narration Audio
- Ambient Audio
- Metadata

---

# Engine Dependency Graph

```
Import Service
      │
      ▼
Universe Builder
      │
      ▼
Universe
      │
      ▼
World State
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
Scene Engine
      │
      ▼
Narration Engine
      │
      ▼
Media Pipeline
```

---

# Interface Rules

Every engine must:

- Expose exactly one public entry point.
- Receive explicit inputs.
- Return explicit outputs.
- Never modify another engine's internal state.
- Never bypass the Runtime Pipeline.
- Never access persistence directly unless explicitly responsible.
- Operate independently and remain replaceable without affecting other engines.