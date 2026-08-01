# `docs/engines/07_relationship_engine.md`

---

# Relationship Engine

**Version:** 1.0

**Status:** Draft

**Owner:** Social Simulation System

---

# 1. Purpose

The Relationship Engine models how every character feels about every other entity in the universe.

Unlike a simple friendship score, relationships in Headcanon are **multi-dimensional, dynamic, and persistent**.

The Relationship Engine answers:

> **"How has this interaction changed the way these entities perceive each other?"**

Relationships influence:

* dialogue
* trust
* cooperation
* conflict
* future decisions
* world simulation

---

# 2. Design Philosophy

Relationships should be

* persistent
* explainable
* incremental
* emotionally grounded
* difficult to change drastically

One conversation should not turn enemies into best friends.

Likewise,

one mistake should not destroy years of trust.

---

# 3. Responsibilities

The Relationship Engine is responsible for

* Creating relationships
* Updating affinity
* Tracking trust
* Tracking respect
* Tracking fear
* Tracking loyalty
* Tracking reputation
* Recording relationship history
* Providing relationship context

It is **not responsible** for

* Character dialogue
* Memory retrieval
* Simulation
* Timeline updates

---

# 4. Inputs

```text
Interaction Result

↓

Participants

↓

World State

↓

Current Memories

↓

Current Relationship
```

---

# 5. Outputs

Example

```json
{
    "relationship_updates":[
        {
            "source":"char_user",

            "target":"char_hermione",

            "trust":+4,

            "respect":+2
        }
    ]
}
```

---

# 6. High-Level Pipeline

```text
Interaction

↓

Determine Participants

↓

Evaluate Impact

↓

Calculate Relationship Changes

↓

Apply Constraints

↓

Store History

↓

Return Updates
```

---

# 7. Internal Architecture

```text
Relationship Engine

├── Relationship Loader

├── Interaction Analyzer

├── Affinity Calculator

├── Trust Calculator

├── Respect Calculator

├── Reputation Manager

├── Relationship Historian

└── Validator
```

---

# 8. Relationship Schema

```json
{
    "source":"char_harry",

    "target":"char_hermione",

    "affinity":92,

    "trust":95,

    "respect":88,

    "fear":3,

    "loyalty":91,

    "reputation":84,

    "relationship_type":"Best Friend",

    "history":[]
}
```

---

# 9. Affinity

Affinity measures

> "How much do I personally like this person?"

Scale

```text
-100

Hatred

↓

0

Neutral

↓

100

Deep Friendship
```

Affinity changes gradually.

---

# 10. Trust

Trust measures

> "Can I rely on this person?"

Examples

```text
Keep Promise

↓

Trust +5

Lie

↓

Trust -12

Protect Me

↓

Trust +10
```

Trust affects

* secrets
* cooperation
* dialogue

---

# 11. Respect

Respect measures

> "Do I admire this person?"

Respect can increase

without friendship.

Example

```text
Snape

↓

Respects

Harry

↓

Doesn't necessarily like him.
```

---

# 12. Fear

Fear measures

> "Am I afraid of this entity?"

Example

```text
Voldemort

↓

Fear

98
```

Fear influences

* speech
* decisions
* avoidance

---

# 13. Loyalty

Loyalty measures commitment.

Example

```text
House Elf

↓

Loyalty

100
```

Unlike trust,

loyalty is difficult to gain.

---

# 14. Reputation

Reputation differs from relationships.

Relationship

Private.

↓

Reputation

Public.

Example

```text
Harry defeats troll.

↓

Entire school

Reputation +12
```

---

# 15. Relationship Types

Automatically inferred.

Examples

```text
Enemy

Acquaintance

Friend

Best Friend

Mentor

Student

Sibling

Parent

Rival

Romantic Interest

Stranger

Trusted Ally
```

Relationship type derives from metrics.

Not manually assigned.

---

# 16. Relationship History

Every major change recorded.

Example

```json
[
    {
        "event":"Saved from troll",

        "trust":+15
    },

    {
        "event":"Shared secret",

        "trust":+8
    }
]
```

History explains current values.

---

# 17. Relationship Decay

Relationships weaken without interaction.

Example

```text
Affinity

70

↓

68

↓

66

↓

64
```

Decay is slow.

Close relationships decay less.

---

# 18. Reinforcement

Repeated positive experiences reinforce bonds.

Example

```text
Study Together

↓

Help Each Other

↓

Protect Each Other

↓

Friendship Strengthens
```

---

# 19. Negative Relationships

Negative interactions accumulate.

Example

```text
Lie

↓

Steal

↓

Insult

↓

Enemy
```

Recovery requires sustained positive actions.

---

# 20. Group Relationships

Relationships propagate.

Example

```text
Harry likes User.

↓

Ron trusts Harry.

↓

Ron slightly trusts User.
```

Propagation is weak.

Never automatic friendship.

---

# 21. Reputation Propagation

Reputation spreads through witnesses.

Example

```text
User defeats basilisk.

↓

Witnesses observe.

↓

School hears.

↓

User reputation increases.
```

No witnesses?

No reputation gain.

---

# 22. Prompt Strategy

Relationship Engine uses

```text
evaluate_relationship_change.txt

calculate_trust.txt

calculate_respect.txt

calculate_reputation.txt

propagate_relationships.txt

validate_relationship.txt
```

Each prompt should perform one calculation.

---

# 23. Validation

Validator checks

✔ Valid entities

✔ Valid scores

✔ No duplicate relationships

✔ Metrics within range

✔ Valid history

Reject inconsistent updates.

---

# 24. Engine Communication

Reads

```text
Interaction Results

Memories

Characters

World State
```

Updates

```text
Relationship Store

Reputation Store
```

Provides

```text
Relationship Context
```

to the Character Engine.

---

# 25. Storage

```text
universes/

    hp_001/

        relationships/

            char_harry.json

            char_hermione.json

            reputation.json
```

Relationship history is stored separately from memories.

---

# 26. Performance Considerations

The engine should

* update only affected relationships
* cache frequently accessed pairs
* avoid recomputing unrelated characters
* batch reputation propagation

This keeps social simulation efficient even in large universes.

---

# 27. Future Extensions

The Relationship Engine supports future systems such as

```text
Romance

Family Trees

Political Alliances

Faction Standing

Mentorship

Jealousy

Influence Networks

Social Circles

Popularity

Leadership
```

without altering the core relationship model.

---

# 28. Example End-to-End Flow

```text
User

↓

Helps Hermione

↓

Trust +5

↓

Affinity +3

↓

Respect +2

↓

New Relationship History

↓

Memory Created

↓

Future Dialogue Changes
```

---

# 29. Summary

The Relationship Engine is the **social fabric** of Headcanon.

Rather than treating characters as isolated agents, it models the evolving bonds between individuals through trust, affinity, respect, fear, loyalty, and reputation. Every meaningful interaction leaves a lasting social impact, ensuring that friendships, rivalries, and alliances develop naturally over time and influence every future conversation and decision within the simulated universe.
