# Cache

## Purpose

The Cache System improves performance by reducing repeated computation and minimizing unnecessary API calls.

Caching is an optimization layer only.

The cache must never become the source of truth. The World State remains the authoritative runtime representation of the universe.

---

# Responsibilities

The Cache System is responsible for

- Reducing LLM requests
- Improving response latency
- Reducing storage reads
- Reusing generated media
- Improving frontend performance

---

# Cache Layers

Headcanon uses multiple cache layers

Frontend Cache

↓

Backend Memory Cache

↓

Persistent Storage

---

# Frontend Cache

Stores

- Current Scene
- Generated Images
- Character Portraits
- UI Assets

The frontend should invalidate cached data whenever the Scene Version changes.

---

# Backend Cache

Stores

- Recently loaded universes
- Current World State
- Character contexts
- Knowledge graph queries
- Frequently used prompt templates

The backend cache should prioritize active sessions.

---

# Media Cache

Generated media should be cached.

Includes

- Scene illustrations
- Character portraits
- Narration audio
- Ambient audio

If identical media already exists, it should be reused instead of regenerated.

---

# Prompt Cache

Frequently used prompts should be loaded into memory during application startup.

Avoid repeated disk reads for static prompt files.

---

# Character Context Cache

Cache recently generated character contexts.

Contents

- Personality
- Relevant memories
- Emotional state
- Relationships
- Current goals

Invalidate after every World State update affecting the character.

---

# Scene Cache

Cache recently generated scenes.

A Scene should only be reused if

- World State Version matches
- Scene Version matches
- Location remains unchanged

Otherwise regenerate the Scene.

---

# Cache Keys

Example cache identifiers

Universe ID

↓

World State Version

↓

Scene ID

↓

Character ID

↓

Prompt Version

Keys should uniquely identify cached resources.

---

# Cache Invalidation

Invalidate cache when

- World State changes
- Timeline advances
- Character moves
- Relationships change
- Memories update
- Prompt version changes

Outdated cached data should never be served.

---

# Expiration

Suggested strategy

Frontend Cache

Current session

Backend Cache

Least Recently Used (LRU)

Media Cache

Long-term

Prompt Cache

Application lifetime

---

# Cache Miss

If requested data is unavailable

↓

Load from storage

↓

Regenerate if necessary

↓

Store in cache

↓

Return result

---

# Performance Goals

The Cache System should

- Reduce repeated LLM calls
- Reduce repeated storage access
- Improve scene generation speed
- Improve interaction latency

Caching should remain transparent to the user.

---

# Future Extensions

Potential improvements

- Distributed cache
- Redis integration
- Predictive scene caching
- Character preloading
- Background media pre-generation

---

# Related Documents

- 02_storage_schema.md
- 06_snapshots.md
- ../universe/09_world_state.md
- ../engines/05_scene_engine.md
- ../engines/02_character_engine.md