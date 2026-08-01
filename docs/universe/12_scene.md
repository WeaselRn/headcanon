# Scene

## Purpose

A Scene represents the user's current view of the universe.

It is the primary data structure exchanged between the backend and frontend during gameplay.

Rather than exposing the complete World State, the backend generates a Scene containing only the information relevant to the user's current location and context.

Every user interaction results in a refreshed Scene.

---

# Responsibilities

The Scene is responsible for

- Displaying the current location
- Showing visible characters
- Showing visible objects
- Presenting narration
- Providing available actions
- Reflecting the latest World State

---

# Scene Lifecycle

Load World State

↓

Determine Current Location

↓

Collect Visible Entities

↓

Generate Narration

↓

Determine Available Actions

↓

Return Scene

---

# Scene Structure

Each Scene contains

- Scene ID
- Universe ID
- Timestamp
- Current Location
- Narration
- Characters
- Objects
- Available Actions
- Environment
- Media Assets
- Metadata

---

# Location

The current location includes

- Location ID
- Name
- Description
- Parent Location
- Connected Locations

Example

Location

Great Hall

Connected

- Entrance Hall
- Courtyard
- Library

---

# Narration

Narration describes the current scene.

It should

- reflect the latest World State
- remain concise
- avoid repeating previous narration
- acknowledge recent events
- maintain the story's tone

Narration is descriptive, not conversational.

---

# Characters

Only characters currently visible to the user are included.

Each character contains

- Character ID
- Name
- Current Emotion
- Current Activity
- Interaction Availability

Hidden or distant characters are omitted.

---

# Objects

Visible interactive objects include

- Object ID
- Name
- Category
- Interaction Options
- Current State

Examples

- Sword
- Potion
- Letter
- Door
- Book

---

# Available Actions

Actions are generated dynamically.

Examples

- Talk
- Observe
- Travel
- Inspect
- Pick Up
- Give
- Use
- Wait

Unavailable actions are omitted.

---

# Environment

Current environmental information

- Time of Day
- Weather
- Lighting
- Ambient Description

Example

Morning

Sunny

Great Hall bustling with students.

---

# Media Assets

Optional generated media

- Scene Illustration
- Narration Audio
- Ambient Audio

Media generation should never block scene creation.

---

# Metadata

Additional information

- Scene Version
- World State Version
- Snapshot ID
- Generation Timestamp

Used for synchronization and debugging.

---

# Scene Refresh

A new Scene is generated when

- User performs an action
- User travels
- Time advances
- Simulation updates the world
- A significant event occurs

The frontend should replace the previous Scene rather than patch individual elements.

---

# Design Principles

A Scene should

- Represent the current moment only
- Never expose hidden information
- Be deterministic for the current World State
- Minimize unnecessary data transfer
- Support future multimedia enhancements

---

# Related Documents

- 09_world_state.md
- 10_events.md
- ../frontend/01_scene_layout.md
- ../frontend/02_navigation.md
- ../engines/05_scene_engine.md
- ../api/03_scene.md