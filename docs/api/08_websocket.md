# WebSocket API

## Purpose

The WebSocket API provides real-time communication between the frontend and backend.

Unlike the REST APIs, which operate on individual requests, the WebSocket connection continuously streams updates whenever the World State changes.

This enables a responsive and immersive experience without requiring the frontend to repeatedly poll the server.

---

# Responsibilities

The WebSocket API is responsible for

- Streaming scene updates
- Streaming simulation progress
- Streaming media generation progress
- Streaming autosave status
- Streaming universe notifications
- Supporting future multiplayer synchronization

---

# Connection Endpoint

GET

/ws/universes/{universe_id}

A WebSocket connection is established after the universe has been loaded.

---

# Connection Lifecycle

Client Connects

↓

Authenticate (future)

↓

Load Universe

↓

Subscribe to Events

↓

Receive Updates

↓

Disconnect

---

# Event Types

The server may emit

- Scene Updated
- Character Updated
- Timeline Updated
- World State Updated
- Simulation Complete
- Autosave Complete
- Media Generation Progress
- Notification

---

# Scene Updated

Sent whenever a new Scene becomes available.

Payload

- Scene ID
- Scene Version
- Current Location
- Timestamp

The frontend should replace the current Scene.

---

# Character Updated

Sent when visible characters change.

Examples

- Character enters
- Character leaves
- Emotion changes
- Activity changes

Only visible character updates should be transmitted.

---

# World State Updated

Sent whenever the World State Version changes.

Contains

- World State Version
- Update Type
- Timestamp

The frontend should synchronize local state.

---

# Timeline Updated

Sent after

- Event completion
- Event cancellation
- Time advancement
- Generated events

Allows the frontend to update timeline-related components.

---

# Simulation Events

Simulation progress may emit

Simulation Started

↓

Simulation Running

↓

Simulation Completed

↓

Scene Updated

This allows the UI to display progress indicators.

---

# Media Generation

Media generation may emit

Queued

↓

Generating

↓

Uploading

↓

Completed

↓

Failed

The Scene remains usable throughout media generation.

---

# Autosave Events

When autosave completes

Return

- Snapshot ID
- Timestamp
- Save Status

Example

{
    "event": "autosave_completed",
    "snapshot_id": "...",
    "timestamp": "..."
}

---

# Notifications

Examples

- Universe Imported
- Snapshot Created
- Media Ready
- Simulation Finished
- Storage Retry
- Update Available

Notifications should be informational only.

---

# Client Events

The client may send

- Ping
- Refresh Scene
- Subscribe
- Unsubscribe

Future versions may support

- Voice Streaming
- Multiplayer Events
- Collaborative Sessions

---

# Error Handling

Possible errors

Invalid Universe

↓

Connection Closed

Simulation Error

↓

Notification

Storage Failure

↓

Retry Notification

Fatal Error

↓

Disconnect

The client should automatically attempt reconnection where appropriate.

---

# Reconnection

If the connection is lost

Reconnect

↓

Verify Universe

↓

Resume Subscription

↓

Receive Latest World State

↓

Continue Session

No gameplay progress should be lost.

---

# Performance

The WebSocket connection should

- Minimize bandwidth
- Send only relevant updates
- Avoid duplicate events
- Batch related updates where possible

Large assets should never be streamed through the WebSocket.

Instead, send asset metadata and download URLs.

---

# Security

Every connection should validate

- Universe ID
- Session
- Authorization (future)

Never transmit

- Internal prompts
- API keys
- Storage credentials
- Hidden World State

Only data visible to the current user should be streamed.

---

# Future Extensions

Potential additions

- Multiplayer universes
- Shared character interactions
- Live NPC movement
- Voice streaming
- Collaborative storytelling
- Real-time world events

---

# Related Documents

- ../runtime_pipeline.md
- ../universe/09_world_state.md
- ../universe/12_scene.md
- ../engines/05_scene_engine.md
- ../engines/10_media_pipeline.md