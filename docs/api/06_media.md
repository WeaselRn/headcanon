# Media API

## Purpose

The Media API manages the generation, retrieval, and lifecycle of multimedia assets associated with a universe.

Media generation is optional and should never block gameplay or world simulation.

The API provides access to scene illustrations, narration, ambient audio, and future media types while maintaining links to the corresponding World State.

---

# Responsibilities

The Media API is responsible for

- Generating media assets
- Retrieving generated assets
- Returning asset metadata
- Tracking generation status
- Managing media lifecycle

---

# Endpoint

POST

/api/v1/universes/{universe_id}/media/generate

Generates media for the current or specified scene.

---

# Request

The request may contain

- Scene ID
- Asset Types
- Generation Options

Example

{
    "scene_id": "scene_021",
    "assets": [
        "image",
        "narration",
        "ambient_audio"
    ]
}

---

# Supported Asset Types

Current

- Scene Illustration
- Narration Audio
- Ambient Audio

Future

- Character Portraits
- Animated Scenes
- Music
- Sound Effects
- Video

---

# Generation Pipeline

Request

↓

Load Scene

↓

Generate Prompt

↓

Generate Assets

↓

Upload to Storage

↓

Save Metadata

↓

Return Asset References

---

# Image Generation

Uses

- Current Scene
- Environment
- Visible Characters
- Visible Objects

The generated illustration should accurately represent the current World State.

---

# Narration Generation

Narration is generated from

- Current Scene
- Environment
- Current Narration

The narration should remain faithful to the existing story tone.

---

# Ambient Audio

Ambient audio is generated using

- Environment
- Weather
- Location
- Active Events

Examples

- Rain
- Forest
- Castle Hall
- Marketplace

---

# Successful Response

Returns

- Asset IDs
- Asset Types
- Generation Status
- Storage URLs
- Metadata

Example

{
    "status": "completed",
    "assets": [
        {
            "type": "image",
            "asset_id": "...",
            "url": "..."
        }
    ]
}

---

# Retrieve Assets

GET

/api/v1/universes/{universe_id}/media

Returns all generated assets belonging to the universe.

Optional filters

- Scene
- Asset Type
- Date

---

# Asset Metadata

Each asset stores

- Asset ID
- Scene ID
- Universe ID
- Asset Type
- Generation Timestamp
- Prompt Version
- Storage Path

---

# Error Responses

400

Invalid Request

404

Universe or Scene Not Found

422

Media Generation Failed

500

Internal Server Error

---

# Performance

Media generation should

- Execute asynchronously
- Support parallel generation
- Never block interaction or simulation
- Cache existing assets where possible

---

# Security

Never expose

- Internal generation prompts
- API credentials
- Storage secrets

Validate all asset requests before retrieval.

---

# Future Extensions

Potential additions

- Video generation
- Character voice synthesis
- Dynamic music
- Cinematic scene transitions
- Asset regeneration

---

# Related Documents

- ../engines/09_narration_engine.md
- ../engines/10_media_pipeline.md
- ../storage/03_media_library.md
- ../storage/04_provenance.md
- ../storage/02_storage_schema.md