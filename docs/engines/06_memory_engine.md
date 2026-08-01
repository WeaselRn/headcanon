# `docs/engines/06_memory_engine.md`

---

# Memory Engine

**Version:** 1.0

**Status:** Draft

**Owner:** Memory & Cognition System

---

# 1. Purpose

The Memory Engine manages what every character remembers, forgets, learns, and emotionally associates with experiences.

Unlike traditional chat history, Headcanon never stores conversations as the source of truth.

Instead, conversations become **memories**.

The Memory Engine answers:

> **"What does this character remember right now?"**

---

# 2. Design Philosophy

The Memory Engine is inspired by human memory.

Characters should

* remember meaningful events
* forget trivial details
* prioritize emotional experiences
* recall relevant memories
* build long-term relationships

Characters should **feel** like they remember the player, not merely replay old messages.

---

# 3. Responsibilities

The Memory Engine is responsible for

* Creating memories
* Retrieving memories
* Ranking memories
* Consolidating memories
* Forgetting memories
* Updating emotional associations
* Storing episodic knowledge
* Building long-term memory

It is **not responsible** for

* Dialogue generation
* Simulation
* Timeline updates
* Scene construction

---

# 4. Inputs

The engine receives

```text
Interaction Result

↓

Current Character

↓

Current World State

↓

Current Emotion
```

---

# 5. Outputs

Example

```json
{
    "new_memories":[...],

    "retrieved_memories":[...],

    "forgotten_memories":[...],

    "importance_updates":[...]
}
```

---

# 6. High-Level Pipeline

```text
Interaction

↓

Should Memory Exist?

↓

Create Memory

↓

Rank Importance

↓

Store

↓

Retrieve Relevant Memories

↓

Forget Low Priority Memories

↓

Return Memory Context
```

---

# 7. Internal Architecture

```text
Memory Engine

├── Memory Creator

├── Importance Evaluator

├── Memory Retriever

├── Memory Consolidator

├── Forgetting Engine

├── Emotional Link Builder

├── Knowledge Extractor

└── Validator
```

---

# 8. Memory Types

Every memory belongs to one category.

## Episodic

Specific events.

Example

```text
User defeated troll with Hermione.
```

---

## Semantic

Facts.

Example

```text
User comes from another world.
```

---

## Emotional

Feelings.

Example

```text
Hermione trusts the user.
```

---

## Procedural (Future)

Skills.

Example

```text
Harry learned new spell.
```

---

# 9. Memory Schema

```json
{
    "id":"",

    "type":"episodic",

    "summary":"",

    "participants":[],

    "location":"",

    "timestamp":"",

    "emotion":"",

    "importance":0,

    "tags":[],

    "references":[]
}
```

---

# 10. Memory Creation

Not every interaction becomes a memory.

Example

User says

```text
Hello.
```

↓

No memory.

---

User says

```text
I'll always protect you.
```

↓

Memory created.

---

# 11. Importance Evaluation

Every memory receives a score.

Scale

```text
0-20

Ignore

21-40

Minor

41-60

Useful

61-80

Important

81-100

Core Memory
```

---

# 12. Importance Factors

Memory importance depends on

```text
Emotional intensity

↓

Novelty

↓

Relationship impact

↓

Goal relevance

↓

World impact

↓

Life-threatening events
```

---

# 13. Retrieval

The engine never returns all memories.

Retrieve

```text
Recent

+

Relevant

+

Emotionally Similar

+

High Importance
```

Only.

---

# 14. Retrieval Example

User asks

```text
Remember when I saved you?
```

↓

Search

```text
Saved

Hero

Danger

User

Hermione
```

↓

Return matching memories.

---

# 15. Emotional Association

Every memory stores emotion.

Example

```json
{
    "summary":"User saved Hermione.",

    "emotion":"Grateful"
}
```

Future retrieval considers emotion.

---

# 16. Memory Consolidation

Many similar memories become one.

Example

```text
Studied Together

↓

Studied Again

↓

Studied Again

↓

Consolidated

↓

User frequently studies with Hermione.
```

This reduces memory explosion.

---

# 17. Forgetting

Characters should forget.

Forget

```text
Low Importance

Old

Repeated

Irrelevant
```

Never forget

```text
Core Memories

Trauma

Relationships

Major Events
```

---

# 18. Memory Decay

Importance slowly decreases.

Example

```text
Importance

52

↓

49

↓

45

↓

40
```

Decay stops at a configurable minimum.

---

# 19. Memory Reinforcement

Recalling a memory strengthens it.

Example

```text
Remember Christmas?

↓

Retrieve

↓

Importance +3
```

Frequently recalled memories persist longer.

---

# 20. Relationship Memories

Relationship memories receive special treatment.

Example

```text
User apologized.

↓

Trust increased.

↓

Relationship memory.
```

These directly influence dialogue.

---

# 21. Knowledge Extraction

Some memories become knowledge.

Example

Memory

```text
User owns a dragon.
```

↓

Knowledge

```text
User owns dragon.
```

Knowledge persists independently.

---

# 22. Contradictory Memories

Characters may remember conflicting information.

Example

```text
User claimed

"I hate magic."

↓

Later

"I love magic."
```

Store both.

Simulation or Character Engine resolves contradictions using timestamps, trust, and evidence.

---

# 23. Memory Limits

Each character has configurable limits.

Example

```text
Recent Memories

100

Core Memories

Unlimited

Semantic Knowledge

Unlimited
```

Prevents uncontrolled growth.

---

# 24. Prompt Strategy

Memory Engine should use specialized prompts.

```text
create_memory.txt

evaluate_importance.txt

retrieve_memories.txt

consolidate_memories.txt

forget_memories.txt

extract_knowledge.txt
```

Each prompt performs one task.

---

# 25. Validation

Validator checks

✔ Valid participants

✔ Valid timestamps

✔ Valid importance

✔ Valid memory type

✔ Valid references

✔ No duplicate IDs

Reject invalid memories.

---

# 26. Engine Communication

Reads

```text
Interaction Results

Characters

Relationships

World State
```

Updates

```text
Character Memory

Knowledge

Relationship Context
```

Provides

```text
Relevant Memory Context
```

to the Character Engine.

---

# 27. Storage

Recommended structure

```text
universes/

    hp_001/

        memories/

            char_harry.json

            char_hermione.json

            char_ron.json
```

Each file contains only that character's memories.

---

# 28. Performance Considerations

The engine should

* index memories by tags
* index by participants
* index by locations
* index by emotion
* cache recently accessed memories

Retrieval should be semantic rather than linear.

---

# 29. Future Extensions

The Memory Engine supports future systems such as

```text
Dreams

False memories

Rumors

Memory corruption

Selective memory loss

Trauma

Flashbacks

Shared memories

Collective memories

Memory editing
```

without changing the core architecture.

---

# 30. Summary

The Memory Engine is the **long-term memory** of Headcanon.

Instead of relying on chat history, it transforms meaningful experiences into structured memories that evolve over time. By creating, reinforcing, consolidating, and forgetting memories in a human-like manner, it enables characters to develop genuine relationships with the user and with each other. This persistent cognitive layer is what makes interactions feel continuous across sessions and allows every playthrough to become a unique history rather than a sequence of disconnected conversations.
