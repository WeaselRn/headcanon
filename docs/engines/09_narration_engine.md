# `docs/engines/09_narration_engine.md`

---

# Narration Engine

**Version:** 1.0

**Status:** Draft

**Owner:** Narrative Presentation System

---

# 1. Purpose

The Narration Engine transforms the raw World State into immersive prose.

Unlike the Character Engine, which speaks **as a character**, the Narration Engine speaks **as the universe itself**.

Its responsibility is to answer:

> **"What is happening around the player right now?"**

The Narration Engine never invents world changes.

It only narrates the current simulation.

---

# 2. Design Philosophy

Narration should be

* immersive
* concise
* descriptive
* dynamic
* canon-faithful
* non-repetitive

Narration should describe the world.

It should never explain mechanics.

---

# 3. Responsibilities

The Narration Engine is responsible for

* Environmental narration
* Action narration
* Transition narration
* Event narration
* Scene introductions
* Atmosphere generation
* Sensory descriptions
* Context summaries

It is **not responsible** for

* Dialogue
* World simulation
* Character reasoning
* Timeline updates

---

# 4. Inputs

```text
Scene

↓

World State

↓

Current Location

↓

Characters

↓

Objects

↓

Events

↓

Recent Mutations
```

---

# 5. Outputs

Example

```json
{
    "title":"Great Hall",

    "narration":"Morning sunlight pours across the enchanted ceiling as students quietly enjoy breakfast. Hermione sits absorbed in a heavy book while Harry laughs with Ron nearby.",

    "ambience":"calm"
}
```

---

# 6. High-Level Pipeline

```text
Scene

↓

Determine Focus

↓

Generate Description

↓

Apply Narrative Style

↓

Return Narration
```

---

# 7. Internal Architecture

```text
Narration Engine

├── Scene Analyzer

├── Focus Selector

├── Description Generator

├── Atmosphere Builder

├── Transition Generator

├── Summary Generator

└── Validator
```

---

# 8. Types of Narration

The engine supports

```text
Scene Introduction

Action Narration

Travel Narration

Environmental Narration

Event Narration

Time Progression

Atmospheric Narration

Recap Narration
```

---

# 9. Scene Introduction

Example

Instead of

```text
Great Hall
```

Generate

```text
The Great Hall hums with quiet conversation beneath its enchanted ceiling, where drifting clouds mirror the morning sky outside. Students gather around the long house tables while owls occasionally swoop overhead carrying letters from home.
```

---

# 10. Action Narration

Example

User

```text
Take Elder Wand
```

↓

Narration

```text
You carefully lift the Elder Wand from its resting place. Several nearby students glance toward you, sensing the significance of the ancient artifact.
```

---

# 11. Travel Narration

Example

```text
Great Hall

↓

Library
```

↓

Narration

```text
Leaving behind the lively chatter of breakfast, you make your way through Hogwarts' winding corridors until the quiet scent of parchment and old books welcomes you into the library.
```

---

# 12. Environmental Narration

Environment affects narration.

Inputs

* Weather
* Time
* Lighting
* Occupants
* Events

Example

Morning

↓

Warm sunlight

Night

↓

Moonlight through stained glass

Rain

↓

Soft droplets against castle windows

---

# 13. Event Narration

Example

```text
Quidditch Match Begins.
```

↓

Narration

```text
A loud cheer erupts from outside as students rush toward the Quidditch pitch. Excitement spreads rapidly through the castle.
```

---

# 14. Transition Narration

Scene changes should feel natural.

Example

```text
Library

↓

Forbidden Forest
```

↓

Narration

```text
The warmth of Hogwarts fades behind you as towering trees swallow the remaining daylight. The forest grows unnervingly quiet.
```

---

# 15. Sensory Details

Narration should incorporate

```text
Sight

Sound

Smell

Temperature

Movement
```

Not every sense every time.

Only those relevant to the scene.

---

# 16. Narrative Perspective

Default perspective

```text
Second Person
```

Example

```text
You step into the Great Hall...
```

This improves immersion.

Future versions may support

* First Person
* Third Person

---

# 17. Dynamic Focus

The engine should focus on what recently changed.

Example

If

Hermione enters

↓

Mention Hermione.

Do not regenerate the entire room description.

---

# 18. Avoid Repetition

If the player remains in the same location

Avoid repeating

```text
The enchanted ceiling reflects the sky...
```

Instead

Mention

* different occupants
* different sounds
* changing activities

---

# 19. Atmosphere

Atmosphere is an independent output.

Examples

```text
Calm

Tense

Mystical

Dangerous

Festive

Lonely

Melancholic

Triumphant
```

Media Engine uses this value.

---

# 20. Recap Narration

The engine can summarize recent events.

Example

```text
Since your last visit, Hermione has moved to the library, Ron has returned from Hogsmeade, and rain has begun falling outside.
```

Useful after loading saved worlds.

---

# 21. Prompt Strategy

The Narration Engine should use specialized prompts.

```text
scene_narration.txt

travel_narration.txt

event_narration.txt

environment_description.txt

scene_recap.txt

validate_narration.txt
```

Each prompt has one responsibility.

---

# 22. Validation

Validator checks

✔ Canon consistency

✔ No spoilers

✔ No invented events

✔ Scene accuracy

✔ Tone consistency

✔ No repeated narration

Reject inaccurate narration.

---

# 23. Engine Communication

Reads

```text
Scene

World State

Environment

Events

Characters

Objects
```

Returns

```text
Narration

Atmosphere

Keywords
```

The Scene Engine embeds this into the Scene object.

---

# 24. Performance Considerations

The Narration Engine should

* cache stable location descriptions
* regenerate only changed sections
* reuse atmospheric phrases intelligently
* minimize LLM calls for unchanged scenes

---

# 25. Future Extensions

The Narration Engine supports

```text
Emotion-aware narration

Multiple writing styles

Narrator personalities

Accessibility narration

Voice-specific scripts

Adaptive pacing

Dynamic recaps

Cinematic narration
```

without changing the core interface.

---

# 26. Example End-to-End Flow

```text
Simulation

↓

Scene Updated

↓

Narration Engine

↓

Determine Changes

↓

Generate Updated Description

↓

Return Narration

↓

Scene Engine

↓

Frontend
```

---

# 27. Summary

The Narration Engine is the **voice of the world**.

It transforms structured simulation data into immersive prose that allows users to experience the universe rather than inspect it. By describing only what is true in the current World State and adapting to changing characters, events, weather, and atmosphere, it ensures that every scene feels alive while remaining completely faithful to the evolving simulation.
