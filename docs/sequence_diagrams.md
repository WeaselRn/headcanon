# Sequence Diagrams

## Purpose

This document describes the runtime interactions between services, engines, storage, and the frontend during common workflows.

It complements `runtime_pipeline.md` by showing the order of communication between system components.

---

# System Components

- Frontend
- FastAPI Backend
- Import Service
- Universe Builder
- World State Manager
- Character Engine
- Interaction Engine
- Simulation Engine
- Scene Engine
- Media Pipeline
- Backblaze B2
- Gemini

---

# Sequence 1 — Import Story

User
    │
    ▼
Frontend
    │ Upload Story
    ▼
Backend
    │
    ▼
Import Service
    │
    ▼
Text Extraction
    │
    ▼
Universe Builder
    │
    ▼
World State Manager
    │
    ▼
Backblaze Storage
    │
    ▼
Return Universe ID

---

# Sequence 2 — Open Universe

Frontend

↓

Backend

↓

Load Universe

↓

Load World State

↓

Scene Engine

↓

Return Initial Scene

---

# Sequence 3 — Character Interaction

User

↓

Frontend

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

World State Manager

↓

Scene Engine

↓

Frontend

---

# Sequence 4 — Travel

Current Scene

↓

Travel Request

↓

Location Validation

↓

World State Update

↓

NPC Updates

↓

Scene Generation

↓

Return New Scene

---

# Sequence 5 — Media Generation

Scene

↓

Media Pipeline

↓

Gemini Image

↓

Narration Engine

↓

Ambient Audio

↓

Backblaze

↓

Return Asset URLs

---

# Sequence 6 — Autosave

Interaction Complete

↓

World State Manager

↓

Snapshot Generator

↓

Backblaze

↓

Metadata Update

---

# Sequence 7 — Resume Session

User

↓

Load Snapshot

↓

Restore World State

↓

Restore Memories

↓

Generate Current Scene

↓

Return Scene

---

# Related Documents

- runtime_pipeline.md
- architecture.md
- storage/02_storage_schema.md
- engines/*