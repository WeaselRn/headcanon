# Scene API

## Purpose

The Scene API is the primary runtime endpoint used by the frontend.

It returns the user's current Scene based on the latest World State.

Rather than exposing the complete universe, the API returns only the information required to render the current location.

The Scene API is expected to be the most frequently called endpoint during gameplay.

---

# Responsibilities

The Scene API is responsible for

- Loading the current Scene
- Returning visible entities
- Returning narration
- Returning available actions
- Returning generated media
- Synchronizing frontend with the World State

---

# Endpoint

GET

/api/v1/universes/{universe_id}/scene

Returns the latest Scene.

---

# Optional Parameters

scene_id

Reload a specific scene.

refresh

Force regeneration of the scene.

include_media

Include generated media assets.

---

# Processing Pipeline

Request

↓

Load World State

↓

Load Current Location

↓

Scene Engine

↓

Generate Narration

↓

Collect Characters

↓

Collect Objects

↓

Generate Available Actions

↓

Return Scene

---

# Successful Response

Returns

- Scene ID
- Scene Version
- Current Location
- Narration
- Characters
- Objects
- Available Actions
- Environment
- Media
- Metadata

Example

{
    "scene_id": "scene_014",
    "scene_version": 42,
    "location": {
        "name": "Great Hall"
    },
    "narration": "...",
    "characters": [],
    "objects": [],
    "actions": [],
    "environment": {},
    "media": {}
}

---

# Character Data

Each visible character contains

- Character ID
- Name
- Portrait
- Current Emotion
- Current Activity
- Interaction Availability

Only visible characters should be returned.

---

# Object Data

Each visible object contains

- Object ID
- Name
- Category
- Current State
- Available Interactions

Hidden objects should not be returned.

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

Only actions valid for the current World State should be returned.

---

# Environment

Return

- Time
- Weather
- Lighting
- Ambient Description

The frontend should not infer environment information.

---

# Media

Optional media assets

- Scene Illustration
- Narration Audio
- Ambient Audio

Media generation is asynchronous.

If media is unavailable, the Scene should still be returned.

---

# Scene Refresh

A new Scene should be generated when

- World State Version changes
- Character locations change
- Objects move
- Timeline advances
- Simulation completes
- User travels

If no changes occur, a cached Scene may be returned.

---

# Validation

Verify

- Universe exists
- World State exists
- Current location exists
- Scene generation succeeds

---

# Error Responses

400

Invalid Request

404

Universe Not Found

409

Scene Generation Failed

500

Internal Server Error

---

# Performance

The Scene API should

- Return within target interaction latency
- Support scene caching
- Minimize payload size
- Avoid redundant regeneration

---

# Security

Never expose

- Hidden characters
- Hidden objects
- Internal simulation state
- Prompt contents
- Future timeline events

The API should only expose information currently observable by the user.

---

# Future Extensions

Potential additions

- Partial scene updates
- Multiplayer synchronization
- Streaming narration
- Live NPC movement
- Weather animation

---

# Related Documents

- ../universe/12_scene.md
- ../frontend/01_scene_layout.md
- ../engines/05_scene_engine.md
- ../runtime_pipeline.md