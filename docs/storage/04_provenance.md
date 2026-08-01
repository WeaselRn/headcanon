# Provenance

## Purpose

Every AI-generated artifact within Headcanon must be reproducible.

The Provenance system records

- where an asset came from
- what produced it
- which world state it belongs to
- which prompts were used
- which model generated it

This allows complete transparency throughout the entire universe lifecycle.

Provenance never stores the asset itself.

It only stores metadata describing its origin.

---

# Goals

The Provenance system exists to provide

- reproducibility
- auditability
- debugging
- model comparison
- regeneration
- research

Every AI output should be explainable.

---

# Scope

Provenance should be recorded for

- universe reconstruction
- character responses
- timeline simulations
- memory updates
- relationship updates
- generated illustrations
- generated narration
- ambient audio

Every LLM or AI call creates provenance.

---

# Provenance Record

Every execution produces one record.

Example

```json
{
  "execution_id": "exec_0042",

  "type": "scene_generation",

  "created_at": "...",

  "pipeline_version": "1.0.0",

  "engine": "Scene Engine",

  "model": "gemini-2.5-flash",

  "prompt": "scene_image_v2",

  "input_snapshot": "snapshot_0008",

  "output_assets": [
    "img_0012"
  ],

  "duration_ms": 1240,

  "status": "success"
}
```

---

# Execution Types

Supported execution types

- import
- universe_builder
- character_response
- interaction
- simulation
- memory_update
- relationship_update
- narration
- image_generation
- ambient_audio
- snapshot_creation

Future execution types may be added.

---

# Pipeline Version

Every execution records

```
Pipeline Version

Engine Version

Prompt Version

Schema Version
```

These versions allow exact replay.

---

# Prompt Tracking

Every AI call stores

```
Prompt Name

↓

Prompt Version

↓

Prompt Hash
```

The hash uniquely identifies the exact prompt used.

Changing one line produces a different hash.

---

# Model Tracking

Record

```
Provider

↓

Model

↓

Temperature

↓

Max Tokens

↓

Generation Config
```

Example

```json
{
  "provider": "Google",

  "model": "gemini-2.5-flash",

  "temperature": 0.6,

  "max_tokens": 8192
}
```

---

# Input Tracking

Each execution records

- universe id
- snapshot id
- character ids
- location id
- interaction id

This identifies the complete input context.

---

# Output Tracking

Each execution records

Generated

- image ids
- narration ids
- audio ids
- timeline events
- memories
- relationship changes

Every output must be traceable.

---

# Error Tracking

Failures are also provenance.

Example

```json
{
  "status": "failed",

  "error": "Model timeout",

  "retry_count": 2
}
```

This helps debugging.

---

# Provenance Chain

Every execution references the previous state.

```
Snapshot 12

↓

Interaction

↓

Simulation

↓

Image

↓

Narration

↓

Snapshot 13
```

The chain should never be broken.

---

# Replay

Given

- source story
- snapshot
- prompts
- models

Headcanon should be capable of reproducing the same pipeline.

Outputs may differ due to nondeterministic models,
but the execution process remains identical.

---

# Storage

Each universe stores

```
provenance/

    exec_0001.json

    exec_0002.json

    exec_0003.json
```

Each execution has its own file.

This avoids a single massive provenance document.

---

# Search

The backend should support querying provenance by

- execution id
- model
- prompt
- engine
- asset
- snapshot
- date

without scanning the entire universe.

---

# Privacy

Provenance must never store

- API keys
- authentication tokens
- user passwords
- personally identifiable information

Only execution metadata should be recorded.

---

# Future Compatibility

Future provenance records may include

- token usage
- latency breakdown
- cost estimation
- carbon footprint
- GPU information
- cache hits
- multimodal inputs

The schema should remain backward compatible.

---

# Design Principles

The Provenance system should be

- deterministic
- immutable
- append-only
- searchable
- reproducible
- auditable

Every AI-generated artifact in Headcanon should have a complete and traceable history.