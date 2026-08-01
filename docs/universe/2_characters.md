# `docs/universe/02_characters.md`

---

# Characters

**Version:** 1.0

**Status:** Draft

**Owner:** Character Engine

---

# 1. Purpose

Characters are the primary autonomous entities within a Headcanon universe.

Unlike traditional NPCs, characters are **persistent world entities** that:

* remember events
* maintain relationships
* pursue goals
* acquire knowledge
* change emotional states
* react to user actions
* influence future events

A character is **not** a prompt.

A character is **structured data interpreted by the Character Engine.**

---

# 2. Design Philosophy

Every character should satisfy five principles.

## Identity

The character must always remain recognizably themselves.

Hermione must always feel like Hermione.

Never ChatGPT pretending to be Hermione.

---

## Consistency

Given identical context,

the character should produce nearly identical reasoning.

---

## Persistence

Characters remember.

Memories survive sessions.

---

## Limited Knowledge

Characters only know what they realistically know.

Harry should not know Voldemort's plans before canon reveals them.

---

## Adaptability

Characters evolve naturally through experiences.

Relationships and emotions change.

Personality does not.

---

# 3. Character Lifecycle

```text
Universe Builder

↓

Character Created

↓

World State Initialization

↓

Interaction

↓

Memory Update

↓

Relationship Update

↓

Simulation

↓

Save Snapshot
```

---

# 4. Character Object

```json
{
  "id": "",
  "name": "",
  "aliases": [],
  "role": "",
  "species": "",
  "age": null,
  "occupation": "",
  "description": "",
  "appearance": {},
  "personality": {},
  "speech": {},
  "morality": {},
  "goals": [],
  "knowledge": {},
  "relationships": [],
  "inventory": [],
  "abilities": [],
  "status": {},
  "memory": {},
  "metadata": {}
}
```

---

# 5. Identity

Identity never changes.

Example

```json
{
    "id":"char_hermione",
    "name":"Hermione Granger",
    "aliases":[
        "Hermione"
    ]
}
```

IDs are immutable.

Names may support aliases.

---

# 6. Role

Defines narrative function.

Examples

```text
Protagonist

Supporting

Mentor

Villain

Merchant

Civilian

Student

Creature

Companion
```

Role helps Simulation Engine assign priorities.

---

# 7. Appearance

Contains descriptive attributes.

Example

```json
{
    "hair":"Brown",
    "eyes":"Brown",
    "height":"165 cm",
    "clothing":"Hogwarts Uniform"
}
```

Used only for media generation.

Never for reasoning.

---

# 8. Personality

Most important section.

Example

```json
{
    "traits":[
        "Logical",
        "Brave",
        "Curious"
    ],

    "strengths":[
        "Research",
        "Planning"
    ],

    "weaknesses":[
        "Perfectionism"
    ]
}
```

Personality is immutable.

Simulation cannot overwrite it.

---

# 9. Speech Profile

Speech controls dialogue.

Example

```json
{
    "style":"Formal",

    "vocabulary":"Advanced",

    "humor":"Rare",

    "catchphrases":[

    ],

    "tone":"Calm"
}
```

Dialogue generation must always respect this profile.

---

# 10. Morality

Defines decision boundaries.

Example

```json
{
    "alignment":"Good",

    "violence":0.2,

    "honesty":0.95,

    "selflessness":0.91
}
```

Simulation uses morality before relationships.

---

# 11. Goals

Characters always possess active goals.

Example

```json
[
    {
        "goal":"Protect Harry",
        "priority":100
    },

    {
        "goal":"Study for exams",
        "priority":82
    }
]
```

Goals evolve.

Core motivations usually do not.

---

# 12. Knowledge

Knowledge is private.

Example

```json
{
    "known_locations":[

    ],

    "known_people":[

    ],

    "known_events":[

    ],

    "known_objects":[
    ]
}
```

Knowledge differs between characters.

---

# 13. Relationships

Relationships store references.

Example

```json
[
    {
        "target":"char_harry",

        "relationship":"Friend",

        "affinity":94
    }
]
```

Detailed behavior defined in

```text
relationships.md
```

---

# 14. Inventory

Characters own items.

Example

```json
[
    "obj_wand",

    "obj_book",

    "obj_key"
]
```

Objects exist independently.

Inventory stores references.

---

# 15. Abilities

Example

```json
[
    "Magic",

    "Potion Brewing",

    "Ancient Runes"
]
```

Abilities determine possible actions.

---

# 16. Status

Status is mutable.

Example

```json
{
    "location":"loc_library",

    "health":"Healthy",

    "emotion":"Focused",

    "energy":82,

    "busy":true
}
```

Simulation updates status constantly.

---

# 17. Memory

Memory is the core feature.

Each memory stores

```json
{
    "id":"mem_001",

    "timestamp":"...",

    "importance":91,

    "summary":"User helped solve potion puzzle.",

    "participants":[
        "char_user",
        "char_hermione"
    ]
}
```

Characters never read chat history.

They read memories.

---

# 18. Memory Types

Three categories.

## Episodic

Events experienced.

```text
User saved me.
```

---

## Semantic

Facts learned.

```text
The user is from another world.
```

---

## Emotional

Feelings.

```text
I trust the user.
```

---

# 19. Memory Importance

Every memory has importance.

Scale

```text
0–20

Forgettable

21–60

Ordinary

61–90

Important

91–100

Core Memory
```

High importance memories are never discarded.

---

# 20. Memory Retrieval

Character Engine retrieves

* recent memories
* relevant memories
* emotional memories

Not every memory.

Example

```text
User asks

"Remember when we met?"

↓

Search memories

↓

Return meeting memory
```

---

# 21. Emotional State

Emotion changes frequently.

Examples

```text
Happy

Curious

Anxious

Angry

Excited

Confused

Sad
```

Emotion influences dialogue.

Not personality.

---

# 22. Decision Priority

Characters decide actions using

```text
World Rules

↓

Morality

↓

Current Goals

↓

Knowledge

↓

Relationships

↓

Emotion

↓

Personality

↓

Speech
```

This order prevents inconsistent behavior.

---

# 23. Dialogue Generation

Character Engine never sends

```text
User

↓

LLM
```

Instead

```text
User

↓

Character Context Builder

↓

Character Prompt

↓

LLM

↓

Dialogue
```

Character Context contains

* personality
* speech
* memories
* knowledge
* relationships
* current world state

---

# 24. Character Prompt Context

Example context

```json
{
    "name":"Hermione",

    "personality":[
        "Logical",
        "Brave"
    ],

    "emotion":"Concerned",

    "location":"Library",

    "active_goal":"Find information",

    "relationship_to_user":71,

    "recent_memories":[]
}
```

Only this context reaches the LLM.

Never the entire universe.

---

# 25. Updating Characters

Interaction Engine never edits

* personality
* identity
* speech

It may update

* memories
* goals
* emotions
* inventory
* relationships
* location
* knowledge

---

# 26. Validation Rules

Every character must satisfy:

✔ Unique ID

✔ Name exists

✔ Personality exists

✔ Speech profile exists

✔ Current location exists

✔ Inventory references valid objects

✔ Relationship targets exist

✔ Memory IDs are unique

✔ Goals have priorities

Reject invalid characters.

---

# 27. Storage

Characters are stored independently.

```text
universes/

    hp_001/

        characters/

            harry.json

            hermione.json

            ron.json

            draco.json
```

This avoids rewriting the entire universe when one character changes.

---

# 28. Engine Responsibilities

Universe Builder

* Creates characters

Character Engine

* Builds character context

Interaction Engine

* Requests dialogue

Simulation Engine

* Updates emotions
* Updates goals
* Updates location
* Updates memories
* Updates relationships

Storage Engine

* Saves character snapshots

---

# 29. Future Extensions

The schema supports future additions such as:

```text
Daily schedules

Friend groups

Factions

Romance

Reputation

Fear system

Habits

Secrets

Internal monologue

Voice embeddings

Animation metadata
```

These additions should extend the schema without breaking existing character definitions.

---

# 30. Summary

Characters are **persistent autonomous agents**, not chat personas.

They are defined by a stable identity, immutable personality, bounded knowledge, evolving memories, changing relationships, and dynamic emotional states.

The Character Engine constructs a focused context from this structured data, ensuring every response remains faithful to the original universe while allowing characters to grow naturally as the user reshapes the world.
