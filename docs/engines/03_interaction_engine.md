# `docs/engines/03_interaction_engine.md`

---

# Interaction Engine

**Version:** 1.0

**Status:** Draft

**Owner:** Interaction System

---

# 1. Purpose

The Interaction Engine is responsible for translating **user intent** into meaningful actions within the universe.

It acts as the bridge between the player and the world.

Unlike a chatbot, the Interaction Engine never generates responses itself.

Instead, it determines:

* what the user is trying to do
* which entities are involved
* which engines should handle the request
* whether the requested action is valid

Every user interaction passes through this engine.

---

# 2. Responsibilities

The Interaction Engine is responsible for:

* Understanding user intent
* Identifying action targets
* Validating possible actions
* Routing requests to appropriate engines
* Creating interaction context
* Returning structured interaction results

It is **not responsible** for:

* Character dialogue
* World simulation
* Timeline mutation
* Media generation
* Relationship calculations

---

# 3. Inputs

The engine receives

```text
Current Scene

↓

World State

↓

User Action

↓

Nearby Entities
```

Example

```text
Current Location

Great Hall

Nearby Characters

Harry

Hermione

Draco

Nearby Objects

Sorting Hat

House Cup

User Input

"Ask Hermione about Snape."
```

---

# 4. Outputs

Example

```json
{
    "intent":"talk",

    "target":"char_hermione",

    "parameters":{
        "topic":"Snape"
    },

    "engine":"CharacterEngine"
}
```

The engine never returns dialogue.

---

# 5. High-Level Pipeline

```text
User Input

↓

Intent Detection

↓

Target Resolution

↓

Action Validation

↓

Context Building

↓

Route Request

↓

Return Result
```

---

# 6. Internal Architecture

```text
Interaction Engine

├── Intent Parser

├── Entity Resolver

├── Action Validator

├── Context Builder

├── Engine Router

└── Response Formatter
```

Each module has one responsibility.

---

# 7. Intent Detection

Determine what the user wants.

Supported intents

```text
Talk

Observe

Inspect

Travel

Take

Drop

Give

Use

Attack

Wait

Follow

Search

Read

Open

Close

Equip

Unequip

Cast Spell

Trade

Craft
```

Future intents can be added without changing the architecture.

---

# 8. Entity Resolution

Every interaction must identify its targets.

Example

```text
Talk to Hermione.
```

↓

```json
{
    "target":"char_hermione"
}
```

Example

```text
Pick up the wand.
```

↓

```json
{
    "target":"obj_elder_wand"
}
```

---

# 9. Ambiguity Resolution

Sometimes multiple entities match.

Example

```text
Talk to the student.
```

Nearby

Harry

Ron

Neville

↓

Interaction Engine returns

```json
{
    "status":"ambiguous",

    "options":[
        "Harry",
        "Ron",
        "Neville"
    ]
}
```

Never guess.

---

# 10. Action Validation

Before routing,

verify

✔ target exists

✔ target visible

✔ target reachable

✔ world rules allow action

✔ character capable

Example

```text
User

↓

Fly

↓

No broom

↓

Reject
```

---

# 11. Context Builder

Create a lightweight interaction context.

Example

```json
{
    "location":"Great Hall",

    "time":"Morning",

    "user":"char_user",

    "target":"char_hermione",

    "intent":"talk"
}
```

Only relevant information is forwarded.

---

# 12. Engine Routing

Intent determines destination.

| Intent   | Destination       |
| -------- | ----------------- |
| Talk     | Character Engine  |
| Observe  | Scene Engine      |
| Travel   | Simulation Engine |
| Use Item | Simulation Engine |
| Inspect  | Scene Engine      |
| Wait     | Simulation Engine |
| Give     | Simulation Engine |
| Attack   | Simulation Engine |

The Interaction Engine coordinates—it does not execute.

---

# 13. Multi-Step Actions

Some actions require multiple engines.

Example

```text
Give Hermione the Elder Wand.
```

↓

```text
Validate

↓

Simulation Engine

↓

Ownership Transfer

↓

Relationship Engine

↓

Character Engine

↓

Dialogue
```

---

# 14. Conversation Flow

Example

```text
User

↓

Talk

↓

Character Engine

↓

Dialogue

↓

Memory Update

↓

Return
```

---

# 15. Travel Flow

Example

```text
User

↓

Travel

↓

Validate Route

↓

Simulation Engine

↓

Update Location

↓

Scene Engine

↓

Return New Scene
```

---

# 16. Object Interaction Flow

Example

```text
User

↓

Inspect Book

↓

Locate Object

↓

Scene Engine

↓

Generate Description
```

---

# 17. Failed Interactions

Example

```text
Talk to Dumbledore.
```

↓

Dumbledore not present.

↓

Return

```json
{
    "success":false,

    "reason":"Target not present."
}
```

Failures should explain why the action cannot occur.

---

# 18. Interaction Priority

When multiple actions are possible

Priority

```text
World Rules

↓

Physical Constraints

↓

Character State

↓

Current Scene

↓

User Intent
```

Impossible actions never reach downstream engines.

---

# 19. Scene Awareness

The Interaction Engine only considers the current scene.

It does not search the entire universe.

Example

Current Scene

```text
Library
```

Searches

* nearby characters
* nearby objects
* nearby exits

Only.

---

# 20. Action Cooldowns

Some actions may be temporarily unavailable.

Example

```text
Cast Spell

↓

Already exhausted

↓

Reject
```

Handled during validation.

---

# 21. Structured Interaction Object

Every action becomes

```json
{
    "interaction_id":"int_001",

    "actor":"char_user",

    "intent":"talk",

    "target":"char_hermione",

    "location":"loc_library",

    "timestamp":"..."
}
```

This object is passed between engines.

---

# 22. Prompt Strategy

Interaction Engine uses lightweight prompts.

```text
parse_intent.txt

resolve_entities.txt

validate_action.txt

build_interaction_context.txt
```

These prompts should be deterministic and structured.

---

# 23. Validation Rules

Every interaction must satisfy

✔ Valid intent

✔ Valid actor

✔ Valid target

✔ Valid location

✔ Reachable target

✔ Rule compliance

✔ Permission granted

Reject invalid interactions immediately.

---

# 24. Engine Communication

Reads

```text
Scene

World State

Nearby Characters

Nearby Objects
```

Calls

```text
Character Engine

Simulation Engine

Scene Engine
```

Returns

```text
Structured Interaction Result
```

---

# 25. Performance Considerations

The engine should:

* avoid scanning the full universe
* cache nearby entities
* resolve entities locally first
* minimize LLM usage for obvious actions

Simple interactions like "look around" or "pick up wand" should often be handled without invoking a large language model.

---

# 26. Future Extensions

The Interaction Engine is designed to support:

```text
Gesture recognition

Voice commands

Companion commands

Group conversations

Combat interactions

Stealth actions

Vehicle control

Cooperative multiplayer

Gesture-based magic
```

without requiring architectural changes.

---

# 27. Summary

The Interaction Engine is the **controller** of Headcanon.

It converts natural language into structured, validated actions that the rest of the system can understand. By separating intent parsing from execution, it keeps the architecture modular, ensures every interaction obeys the world's rules, and provides a consistent entry point for all user actions—whether they're speaking to a character, exploring a location, manipulating an object, or altering the course of the universe.
