# Simulation API

## Purpose

The Simulation API is responsible for advancing the universe beyond direct user interactions.

It processes world events, NPC behavior, timeline progression, environmental changes, and autonomous character decisions to ensure the universe continues evolving naturally.

Unlike the Interaction API, the Simulation API may execute without direct user input.

---

# Responsibilities

The Simulation API is responsible for

- Advancing the simulation
- Executing pending events
- Updating NPC behaviour
- Advancing the timeline
- Applying world rule changes
- Updating the World State
- Generating the next Scene

---

# Endpoint

POST

/api/v1/universes/{universe_id}/simulate

---

# Request

The request may contain

- Simulation Mode
- Time Advance
- Trigger
- Target Event (optional)

Example

{
    "mode": "advance_time",
    "minutes": 30
}

---

# Simulation Modes

Supported modes

Advance Time

Run the simulation for a specified duration.

Single Tick

Execute one simulation cycle.

Process Events

Evaluate pending and active events.

Refresh World

Recalculate the current World State.

Automatic

Used internally after interactions.

---

# Processing Pipeline

Request

↓

Load World State

↓

Evaluate Pending Events

↓

Update NPC Behaviour

↓

Resolve Conflicts

↓

Advance Timeline

↓

Update Relationships

↓

Update Memories

↓

Update World State

↓

Generate Scene

↓

Return Result

---

# Simulation Tick

Each simulation tick may update

- Character locations
- Character activities
- Character emotions
- Relationships
- Active events
- Pending events
- Object ownership
- Environment
- Timeline

---

# Event Processing

For every pending event

Verify

- Prerequisites
- World Rules
- Character Availability
- Timeline Consistency

If valid

↓

Activate Event

↓

Execute Consequences

↓

Update World State

---

# NPC Behaviour

Each NPC may

- Move
- Talk
- Rest
- Travel
- Pursue goals
- React to nearby events

NPC behaviour should remain consistent with

- Personality
- Memories
- Relationships
- Emotional state
- World rules

---

# Timeline Updates

Simulation may

- Advance time
- Complete events
- Generate new events
- Cancel invalid events

Timeline consistency must always be preserved.

---

# Successful Response

Returns

- Updated World State Version
- Timeline Version
- Triggered Events
- Updated Scene
- Autosave Status

Example

{
    "world_state_version": 52,
    "timeline_version": 14,
    "events_triggered": 3,
    "scene": { ... },
    "autosaved": true
}

---

# Error Responses

400

Invalid Simulation Request

404

Universe Not Found

409

Timeline Conflict

422

Simulation Failed

500

Internal Server Error

---

# Performance

The Simulation API should

- Execute efficiently
- Support asynchronous processing
- Avoid unnecessary world updates
- Generate scenes only when required

---

# Security

Simulation must never

- Violate world rules
- Reveal hidden information
- Create invalid references
- Corrupt the World State

Every simulation result must be validated before persistence.

---

# Future Extensions

Potential additions

- Background simulation
- Scheduled world updates
- Multiplayer synchronization
- Dynamic weather systems
- Economy simulation
- AI-controlled factions

---

# Related Documents

- ../engines/04_simulation_engine.md
- ../engines/08_timeline_engine.md
- ../universe/09_world_state.md
- ../universe/10_events.md
- ../runtime_pipeline.md