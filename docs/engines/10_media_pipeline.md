# `docs/engines/10_media_pipeline.md`

---

# Media Pipeline

**Version:** 1.0

**Status:** Draft

**Owner:** Multimedia Generation System

---

# 1. Purpose

The Media Pipeline transforms important moments inside the Headcanon universe into persistent multimedia assets.

Unlike the rest of Headcanon, **media generation is optional**.

The universe exists independently of images, narration, and audio.

The Media Pipeline simply visualizes and preserves memorable moments.

It answers:

> **"How should this moment be experienced and remembered?"**

---

# 2. Design Philosophy

Media generation should be

* optional
* asynchronous
* reproducible
* persistent
* provenance-aware
* faithful to the current World State

Media must never invent world changes.

It only visualizes existing ones.

---

# 3. Responsibilities

The Media Pipeline is responsible for

* Scene illustration generation
* Narration generation
* Ambient audio generation
* Metadata generation
* Provenance tracking
* Asset storage
* Asset retrieval
* Asset versioning

It is **not responsible** for

* World simulation
* Dialogue
* Character reasoning
* Timeline updates

---

# 4. Inputs

```text
Scene

↓

Narration

↓

Characters

↓

Environment

↓

Atmosphere

↓

Asset Request
```

---

# 5. Outputs

```json
{
    "scene_id":"scene_014",

    "image":"scene014.webp",

    "narration":"scene014.mp3",

    "ambience":"greathall_morning.mp3",

    "metadata":"scene014.json",

    "provenance":"scene014_provenance.json"
}
```

---

# 6. High-Level Pipeline

```text
Scene

↓

Media Request

↓

Image Prompt

↓

Image Generation

↓

Narration Generation

↓

Ambient Audio

↓

Metadata

↓

Upload to B2

↓

Return Asset References
```

---

# 7. Internal Architecture

```text
Media Pipeline

├── Prompt Builder

├── Image Generator

├── Narration Generator

├── Ambient Audio Generator

├── Metadata Builder

├── Provenance Builder

├── Storage Manager

└── Validator
```

Each module performs exactly one task.

---

# 8. Asset Types

Supported assets

```text
Illustration

Narration

Dialogue Audio

Ambient Audio

Metadata

Provenance

Thumbnail

Preview
```

Future assets can be added independently.

---

# 9. Image Generation

The Scene Engine sends

```text
Location

↓

Characters

↓

Objects

↓

Atmosphere

↓

Current Activity
```

↓

Prompt Builder

↓

Gemini Image

Example

```text
The Great Hall at sunrise.

Harry Potter and Hermione Granger are eating breakfast while owls fly overhead.

Warm cinematic lighting.

Fantasy illustration.
```

---

# 10. Narration Generation

Narration Engine produces

```text
Scene Description
```

↓

Edge TTS

↓

MP3

Narration always matches the current scene.

---

# 11. Ambient Audio

Generated from

```text
Weather

↓

Location

↓

Time

↓

Atmosphere
```

Examples

```text
Forest

↓

Birds

Wind

Leaves
```

```text
Great Hall

↓

Students

Plates

Conversation

Owls
```

Ambient audio loops.

---

# 12. Metadata

Every asset includes metadata.

Example

```json
{
    "scene":"Great Hall",

    "characters":[
        "Harry",
        "Hermione"
    ],

    "weather":"Sunny",

    "time":"Morning",

    "generated_at":"..."
}
```

---

# 13. Provenance

Every generated asset stores

```json
{
    "generated_by":"Gemini",

    "prompt_hash":"...",

    "universe_snapshot":14,

    "scene":"scene_014",

    "timestamp":"..."
}
```

Allows reproducibility.

---

# 14. Asset Versioning

If the scene changes

Create

```text
scene014_v2.webp
```

Do not overwrite.

Every generated asset is immutable.

---

# 15. Storage Layout

Recommended B2 structure

```text
universes/

    hp_001/

        assets/

            images/

                scene001.webp

                scene002.webp

            narration/

                scene001.mp3

            ambience/

                greathall_morning.mp3

            metadata/

                scene001.json

            provenance/

                scene001.json
```

---

# 16. Asset Requests

Media generation may be triggered by

```text
User

↓

Generate Illustration
```

or automatically

```text
Major Event

↓

Generate Scene
```

The pipeline should remain optional.

---

# 17. Asset Caching

Before generating

Check

```text
Scene Hash

↓

Existing Asset?

↓

Return Cached Version
```

Avoid regenerating identical scenes.

---

# 18. Prompt Builder

The Prompt Builder converts structured data into model-specific prompts.

Input

```text
Scene Object
```

↓

Output

```text
Image Prompt

Narration Prompt

Audio Prompt
```

Each model receives only what it needs.

---

# 19. Validation

Validator checks

✔ Asset generated successfully

✔ Metadata exists

✔ Provenance exists

✔ Upload successful

✔ Scene matches snapshot

Reject incomplete asset bundles.

---

# 20. Error Recovery

If image generation fails

Retry only

```text
Image Generator
```

If narration fails

Retry

```text
Narration Generator
```

Never regenerate successful assets.

---

# 21. Engine Communication

Reads

```text
Scene

Narration

Characters

Environment

Atmosphere
```

Calls

```text
Gemini Image

↓

Edge TTS

↓

Backblaze B2
```

Returns

```text
Asset References
```

---

# 22. Performance Considerations

The Media Pipeline should

* execute asynchronously
* queue generation jobs
* cache identical requests
* compress assets before upload
* upload in parallel when possible

Media generation should never block gameplay.

---

# 23. Security & Provenance

Every generated asset should record

* originating universe
* originating snapshot
* generation timestamp
* model used
* prompt hash
* asset checksum

This ensures traceability and reproducibility.

---

# 24. Future Extensions

The pipeline supports future capabilities such as

```text
Video generation

Animation

Character voice cloning

Music generation

3D environments

Interactive panoramas

AR scenes

VR environments

Asset editing
```

without changing the surrounding architecture.

---

# 25. Example End-to-End Flow

```text
User

↓

Generate Scene

↓

Scene Engine

↓

Narration Engine

↓

Media Pipeline

↓

Build Prompts

↓

Gemini Image

↓

Edge TTS

↓

Metadata

↓

Upload to Backblaze

↓

Return Asset URLs

↓

Frontend Displays Scene
```

---

# 26. Integration with Backblaze

Backblaze B2 is the persistent media layer.

It stores

```text
Illustrations

Narrations

Ambient Audio

Metadata

Provenance

Snapshots
```

The Media Pipeline should treat B2 as the authoritative media repository.

---

# 27. Summary

The Media Pipeline is the **creative output layer** of Headcanon.

It transforms structured scenes into rich multimedia experiences without affecting the underlying simulation. By generating illustrations, narration, and ambient audio asynchronously while preserving metadata, provenance, and immutable versions, it allows users to revisit the most meaningful moments of their evolving universe as lasting, cinematic memories.
