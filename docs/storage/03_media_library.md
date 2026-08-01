# Media Library

## Purpose

The Media Library is the permanent registry of every AI-generated asset
associated with a universe.

Unlike the filesystem, which stores the actual files, the Media Library stores
metadata describing each asset.

This enables efficient lookup, filtering, history, and provenance without
scanning storage.

The Media Library never stores binary data.

---

# Goals

The Media Library should

- index every generated asset
- maintain relationships between assets and world state
- preserve historical versions
- enable replay of important moments
- support future asset types

---

# Asset Types

Supported asset types

- Illustration
- Narration
- Ambient Audio
- Thumbnail

Future types

- Video
- Music
- Animation
- 3D Model
- Voice Conversation
- World Map

---

# Media Index

File

```

media_index.json

```

This file acts as the central catalog.

Example

```json
{
  "assets": []
}
```

---

# Media Asset

Each asset contains

```json
{
  "asset_id": "img_00024",

  "type": "image",

  "title": "Breakfast in the Great Hall",

  "description": "Harry and Hermione eating breakfast.",

  "path": "media/images/img_00024.png",

  "created_at": "...",

  "scene_id": "scene_14",

  "snapshot_id": "snapshot_0008",

  "character_ids": [
    "Harry",
    "Hermione"
  ],

  "location_id": "Great Hall",

  "generated_by": "gemini-image",

  "prompt_version": "v2"
}
```

---

# Scene Association

Every asset belongs to exactly one scene.

```

Scene

↓

Image

↓

Narration

↓

Ambient Audio

```

A scene may have multiple assets.

---

# Snapshot Association

Every generated asset references the snapshot that created it.

Example

```

Snapshot 12

↓

Scene Image

↓

Narration

↓

Audio

```

This allows perfect replay of historical moments.

---

# Character Association

Assets reference all visible or participating characters.

Example

```json
[
  "Harry",
  "Hermione",
  "Ron"
]
```

This enables

- character galleries
- search
- filtering

---

# Location Association

Every asset references its location.

Example

```

Great Hall

Forbidden Forest

Diagon Alley

```

This enables location galleries.

---

# Prompt Version

Each asset records

- image prompt version
- narration prompt version
- engine version

This allows regeneration using newer models.

Example

```json
{
  "prompt_version": "image_v3",

  "engine_version": "2.1.0"
}
```

---

# Regeneration

Assets are immutable.

If regenerated,

create a new asset.

Never overwrite.

Example

```

img_0042.png

↓

User regenerates

↓

img_0043.png

```

The latest version becomes active.

Older versions remain accessible.

---

# Active Asset

Each scene records

```

Current Illustration

Current Narration

Current Ambience

```

Switching versions changes only the reference.

Assets themselves remain unchanged.

---

# Search

The Media Library should support searching by

- character
- location
- snapshot
- scene
- asset type
- creation date

without scanning storage.

---

# Gallery Views

The frontend should support

Universe Gallery

↓

Location Gallery

↓

Character Gallery

↓

Timeline Gallery

↓

Snapshot Gallery

All views are powered by the Media Library.

---

# Deletion

Deleting an asset should

- remove it from the media index
- archive metadata
- optionally delete the underlying file

Deleted assets should never silently disappear from provenance.

---

# Future Compatibility

The schema should support future fields such as

- camera angle
- art style
- voice actor
- duration
- language
- subtitles
- animation metadata

without breaking existing assets.

---

# Storage Principles

Every media asset should be

- immutable
- versioned
- searchable
- traceable
- reproducible

The Media Library is the authoritative registry for all generated media.