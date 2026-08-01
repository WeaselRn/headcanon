# `docs/universe/06_relationships.md`

---

# Relationships

**Version:** 1.0

**Status:** Draft

**Owner:** Character Engine / Simulation Engine

---

# 1. Purpose

Relationships define how every entity in the universe perceives every other entity.

Unlike a simple friendship meter, relationships influence:

* dialogue
* trust
* cooperation
* emotional responses
* future decisions
* story evolution
* simulation outcomes

Relationships are **dynamic**, continuously evolving through interactions.

---

# 2. Design Philosophy

Relationships must satisfy six principles.

## Directional

Relationships are not always symmetrical.

Example

```text
Harry trusts Snape.

Snape does not trust Harry.
```

Each direction is stored independently.

---

## Persistent

Relationships survive sessions.

---

## Gradual

Relationships evolve over time.

Large changes require meaningful events.

---

## Explainable

Every major relationship change should have a recorded cause.

---

## Multi-dimensional

Relationships are more than a single score.

---

## Universal

Characters can form relationships with:

* characters
* factions
* locations
* objects
* even the player

---

# 3. Relationship Lifecycle

```text
Universe Builder

↓

Extract Canon Relationships

↓

Initialize Scores

↓

Interaction

↓

Simulation

↓

Relationship Update

↓

Memory Update

↓

Save Snapshot
```

---

# 4. Relationship Object

```json
{
  "source": "",
  "target": "",
  "type": "",
  "scores": {},
  "history": [],
  "last_updated": "",
  "metadata": {}
}
```

---

# 5. Source & Target

Relationships always reference IDs.

Example

```json
{
    "source":"char_harry",
    "target":"char_hermione"
}
```

Never store names.

---

# 6. Relationship Types

Possible types

```text
Friend

Enemy

Family

Mentor

Student

Ally

Neutral

Romantic

Rival

Employer

Follower

Companion

Stranger
```

Type is descriptive.

Behavior comes from scores.

---

# 7. Relationship Scores

Relationships are multidimensional.

```json
{
    "trust":92,

    "respect":88,

    "affection":81,

    "fear":4,

    "suspicion":11,

    "loyalty":90
}
```

Avoid reducing everything to one number.

---

# 8. Trust

Represents belief in another person's intentions.

Examples

```text
0

Will never believe.

↓

50

Uncertain.

↓

100

Absolute trust.
```

---

# 9. Respect

Measures admiration.

High respect does not imply friendship.

Example

```text
Harry

↓

Respects Snape's skill.

↓

Still dislikes him.
```

---

# 10. Affection

Represents emotional closeness.

Examples

```text
Friendship

Love

Care

Companionship
```

---

# 11. Fear

Represents intimidation.

Example

```text
Neville

↓

Snape

↓

Fear

95
```

---

# 12. Suspicion

Represents uncertainty.

Example

```text
Hermione

↓

New User

↓

Suspicion

40
```

Suspicion naturally decreases with positive interactions.

---

# 13. Loyalty

Represents willingness to act.

Example

```text
Ron

↓

Harry

↓

Loyalty

97
```

High loyalty affects Simulation decisions.

---

# 14. Relationship Scale

Every score ranges

```text
0

None

↓

25

Weak

↓

50

Neutral

↓

75

Strong

↓

100

Absolute
```

---

# 15. Relationship History

Every significant update is stored.

Example

```json
[
    {
        "event":"Saved from troll",

        "change":"+30 Trust"
    },

    {
        "event":"Shared secret",

        "change":"+15 Affection"
    }
]
```

History explains current values.

---

# 16. Canon Relationships

Universe Builder extracts initial values.

Example

```text
Harry

↓

Hermione

Trust

70
```

---

# 17. Dynamic Updates

Simulation modifies relationships.

Example

```text
User

↓

Insults Draco

↓

Draco

Trust

-10

↓

Suspicion

+20

↓

Fear

0
```

---

# 18. Relationship Decay

Not every relationship remains static.

Example

```text
Years pass

↓

No interaction

↓

Affection

Slowly decreases
```

Decay rates depend on relationship type.

---

# 19. Relationship Growth

Repeated positive interactions strengthen relationships gradually.

Example

```text
Help Hermione study

↓

+2 Trust

↓

Help again

↓

+2 Trust

↓

Save Hermione

↓

+25 Trust
```

Small actions accumulate.

Major actions produce larger changes.

---

# 20. Relationship Limits

Simulation should clamp scores.

```text
Minimum

0

Maximum

100
```

Never exceed bounds.

---

# 21. User Relationships

The player is simply another character.

Example

```json
{
    "source":"char_hermione",

    "target":"char_user",

    "trust":61
}
```

No special logic.

---

# 22. Relationship Graph

Relationships form a directed graph.

Example

```text
Harry

│

├── Hermione

├── Ron

└── Draco

Hermione

│

├── Harry

├── Ron

└── User
```

Graph queries enable reasoning.

---

# 23. Simulation Priority

Relationship updates consider

```text
World Rules

↓

Current Event

↓

Memory Importance

↓

Morality

↓

Relationship Scores

↓

Emotion
```

Relationships alone never determine behavior.

---

# 24. Dialogue Influence

Character Engine uses relationships to modify responses.

Example

Trust = 90

```text
"I'm glad you're here."
```

Trust = 15

```text
"I don't know why I should tell you that."
```

Same personality.

Different attitude.

---

# 25. Memory Integration

Relationships and memories reinforce each other.

Example

```text
Positive memory

↓

Trust increases

↓

Future dialogue changes
```

Conversely,

```text
Betrayal

↓

Negative memory

↓

Trust decreases

↓

Simulation changes
```

---

# 26. Validation Rules

Every relationship must satisfy

✔ Valid source

✔ Valid target

✔ Valid relationship type

✔ Scores between 0–100

✔ No duplicate edges

✔ Valid history

Reject invalid relationships.

---

# 27. Storage

```text
universes/

    hp_001/

        relationships/

            relationships.json
```

Large universes may shard by character.

Example

```text
harry.json

hermione.json

draco.json
```

---

# 28. Engine Responsibilities

Universe Builder

* Extract canonical relationships
* Initialize scores

Character Engine

* Read relationships
* Build dialogue context

Simulation Engine

* Update scores
* Record history
* Apply decay

Interaction Engine

* Trigger relationship changes

Storage Engine

* Persist updates

---

# 29. Future Extensions

The relationship system supports future additions.

```text
Romance progression

Family trees

Political alliances

Guild reputation

Faction standing

Mentorship

Social influence

Popularity

Marriage

Betrayal probability
```

These extend the model without replacing the core relationship graph.

---

# 30. Example

Initial State

```text
Harry → Hermione

Trust: 72

Respect: 83

Affection: 68
```

User Interaction

```text
The user helps Hermione solve a dangerous magical puzzle.
```

Simulation Result

```text
Harry → User

Trust +5

Hermione → User

Trust +18

Affection +8

Suspicion -12

History

"User solved enchanted puzzle together."
```

Future conversations now naturally reflect these updated values.

---

# 31. Summary

Relationships are **living social connections**, not static affinity scores.

They combine trust, respect, affection, fear, suspicion, loyalty, and historical context to model how characters genuinely feel about one another. As users interact with the world, relationships evolve gradually, shaping dialogue, cooperation, conflict, and future events while preserving each character's core personality. This relationship graph forms the social backbone of the Headcanon universe.
