# World State

## Purpose

The World State represents the live, mutable version of a reconstructed universe.

While the Universe Model stores the canonical structure extracted from the source story, the World State stores everything that changes as users interact with the universe.

Every interaction, simulation, event, or decision updates the World State.

It is the primary source of truth during runtime.

---

# Responsibilities

The World State is responsible for:

- Tracking all mutable entities
- Maintaining character locations
- Tracking inventories
- Updating relationships
- Recording emotional changes
- Managing active events
- Advancing the timeline
- Providing the current scene
- Supporting save and restore

---

# Relationship with Universe Model

Universe Model

- Static
- Created once
- Canonical
- Never modified

↓

World State

- Dynamic
- Updated continuously
- Represents current reality

---

# Components

The World State consists of

- Current Time
- Active Scene
- Character States
- Location States
- Object States
- Relationship States
- Active Events
- Pending Events
- Timeline Progress
- Global Variables

---

# Character States

Each character contains

- Character ID
- Current Location
- Emotional State
- Inventory
- Active Goal
- Current Activity
- Memories
- Relationships
- Health / Status

Example

Harry Potter

Location:
Great Hall

Emotion:
Curious

Inventory:
Wand
Marauder's Map

Current Goal:
Find Hermione

---

# Location States

Each location stores

- Characters Present
- Objects Present
- Environmental State
- Current Events
- Accessibility

Example

Great Hall

Characters

- Harry
- Hermione
- Draco

Objects

- Tables
- Food
- Owl Post

Environment

Morning

Accessible

Yes

---

# Object States

Objects maintain

- Current Owner
- Current Location
- Condition
- Visibility
- Interaction State

Examples

Sword

Owner:
User

Condition:
Intact

Visibility:
Equipped

---

# Relationship States

Relationships are mutable.

Stored as

Character A

↓

Character B

↓

Relationship Value

↓

Trust

↓

Affinity

↓

Respect

↓

Fear

Relationship values change through simulation.

---

# Active Events

Events currently affecting the world.

Each event stores

- Event ID
- Participants
- Location
- Trigger
- Current Status
- Expected Outcome

---

# Pending Events

Future events waiting for activation.

Examples

- Hogwarts Feast
- Quidditch Match
- Dragon Attack

Simulation determines whether they occur.

---

# Timeline Progress

Tracks

Current Chapter

Current Day

Current Time

Completed Events

Cancelled Events

Generated Events

---

# Global Variables

Universe-wide information

Examples

Current Weather

Season

Time of Day

Political State

War Status

Magic Stability

---

# State Updates

Every successful interaction follows:

User Action

↓

Simulation

↓

State Update

↓

Scene Refresh

↓

Autosave

---

# Consistency Rules

The World State must always satisfy

- One character cannot exist in multiple locations.
- One object cannot have multiple owners.
- Timeline remains chronological.
- World rules are never violated.
- All references remain valid.

---

# Persistence

The World State is saved

- After interactions
- After simulations
- Before media generation
- Before session exit
- During automatic checkpoints

Snapshots are versioned and stored separately.

---

# Related Documents

- 01_universe_schema.md
- 07_timeline.md
- 10_events.md
- 11_inventory.md
- 15_snapshot_schema.md
- ../engines/04_simulation_engine.md
- ../engines/08_timeline_engine.md