# Interaction API

## Purpose

The Interaction API processes all user actions within a universe.

It serves as the primary gameplay endpoint, receiving user intent, validating actions, executing simulation, updating the World State, and returning the newly generated Scene.

Every meaningful interaction passes through this API.

---

# Responsibilities

The Interaction API is responsible for

- Receiving user actions
- Validating interactions
- Calling the Character Engine
- Running world simulation
- Updating the World State
- Creating memories
- Updating relationships
- Advancing the timeline
- Returning the updated Scene

---

# Endpoint

POST

/api/v1/universes/{universe_id}/interact

---

# Request

The request contains

- Universe ID
- Current Scene ID
- User Action
- Target (optional)
- Context (optional)

Example

{
    "scene_id": "scene_021",
    "action": "talk",
    "target": "hermione",
    "message": "What do you think about Snape?"
}

---

# Supported Actions

Examples

- Talk
- Ask
- Observe
- Inspect
- Travel
- Pick Up
- Drop
- Give
- Use
- Wait
- Attack
- Follow

The list is extensible.

---

# Processing Pipeline

Request

↓

Action Validation

↓

Interaction Engine

↓

Character Engine

↓

Simulation Engine

↓

Memory Engine

↓

Relationship Engine

↓

Timeline Engine

↓

World State Update

↓

Scene Engine

↓

Return Updated Scene

---

# Action Validation

Before processing

Verify

- Universe exists
- Scene exists
- Target exists
- Action is valid
- World rules allow the action

Invalid actions should never modify the World State.

---

# Character Interaction

If the action targets a character

Load

- Personality
- Memories
- Emotional State
- Relationships
- Current Goals

Generate a response consistent with the character.

---

# World Updates

A successful interaction may update

- Character locations
- Relationships
- Memories
- Emotional states
- Inventory
- Timeline
- Active events

Every successful update increments the World State Version.

---

# Successful Response

Returns

- Updated Scene
- World State Version
- Timeline Version
- Triggered Events
- Snapshot Status

Example

{
    "scene": { ... },
    "world_state_version": 43,
    "events": [],
    "autosaved": true
}

---

# Error Responses

400

Invalid Action

404

Universe or Target Not Found

409

World Rule Violation

422

Simulation Failed

500

Internal Server Error

---

# Idempotency

Interactions are not idempotent.

Submitting the same interaction multiple times may produce different outcomes depending on the evolving World State.

Clients should avoid retrying interactions automatically.

---

# Performance

The Interaction API should

- Respond within target gameplay latency
- Execute simulation efficiently
- Trigger media generation asynchronously
- Return the updated Scene immediately

---

# Security

Never allow

- Actions violating world rules
- Direct World State manipulation
- Hidden entity access
- Unauthorized simulation changes

Every request must be validated before simulation.

---

# Future Extensions

Potential additions

- Multiplayer interactions
- Cooperative actions
- Voice interactions
- Batch interactions
- AI companion actions

---

# Related Documents

- ../engines/03_interaction_engine.md
- ../engines/04_simulation_engine.md
- ../engines/06_memory_engine.md
- ../engines/07_relationship_engine.md
- ../universe/09_world_state.md
- ../universe/12_scene.md
- ../runtime_pipeline.md