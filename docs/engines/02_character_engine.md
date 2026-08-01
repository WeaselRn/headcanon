# `docs/engines/02_character_engine.md`

---

# Character Engine

**Version:** 1.0

**Status:** Draft

**Owner:** Character AI System

---

# 1. Purpose

The Character Engine is responsible for making every character feel alive.

It is **not** a chatbot.

It is a reasoning system that constructs a character's current state from the Universe and World State, then generates responses that remain faithful to the original story.

The Character Engine never invents personalities.

It interprets them.

---

# 2. Responsibilities

The Character Engine is responsible for:

* Loading character data
* Loading relevant memories
* Loading current world state
* Loading nearby entities
* Building character context
* Generating dialogue
* Updating memories
* Updating emotional state
* Updating knowledge

It is **not responsible** for:

* World simulation
* Timeline updates
* Relationship calculations
* Media generation
* Scene construction

---

# 3. Inputs

The Character Engine receives:

```text
Universe

↓

Character ID

↓

Current World State

↓

Current Scene

↓

User Action
```

---

# 4. Outputs

The engine returns

```text
Dialogue

+

Internal Thoughts

+

Emotion Changes

+

Memory Updates

+

Knowledge Updates

+

Requested World Actions
```

Example

```json
{
    "dialogue":"That's actually a fascinating idea.",

    "emotion":"Curious",

    "new_memories":[...],

    "knowledge_updates":[...],

    "requested_actions":[]
}
```

---

# 5. High-Level Pipeline

```text
User Action

↓

Load Character

↓

Build Context

↓

Reason

↓

Generate Dialogue

↓

Generate Internal State

↓

Generate Memory Updates

↓

Return Response
```

---

# 6. Internal Architecture

```text
Character Engine

├── Character Loader

├── Context Builder

├── Memory Retriever

├── Knowledge Retriever

├── Emotion Evaluator

├── Dialogue Generator

├── Memory Updater

├── Knowledge Updater

└── Validator
```

Every module performs exactly one task.

---

# 7. Character Loading

Load immutable data

```text
Identity

Personality

Speech

Morality

Goals

Abilities
```

Then load mutable data

```text
Emotion

Location

Inventory

Relationships

Knowledge

Memories
```

---

# 8. Context Builder

The Context Builder is the most important module.

It prepares the exact information the LLM needs.

Never send the entire universe.

Instead

```text
Character

+

Nearby World

+

Relevant Memories

+

Relationships

+

Current Goal

+

User Action
```

↓

LLM

---

# 9. Context Window

A typical context looks like

```text
Hermione

Location:
Library

Emotion:
Focused

Current Goal:
Research Nicolas Flamel

Nearby Characters

Harry

Ron

Nearby Objects

Ancient Books

Current Relationship to User

72

Relevant Memories

User helped locate restricted section.

User enjoys asking difficult questions.
```

This context is deterministic.

---

# 10. Memory Retrieval

Do not retrieve every memory.

Retrieve

Recent memories

↓

Relevant memories

↓

Important memories

Example

```text
User asks

Remember yesterday?

↓

Retrieve

Yesterday memories only.
```

---

# 11. Knowledge Retrieval

Characters only know facts available to them.

Example

Hermione

knows

```text
Hogwarts

Magic

Harry

Ron
```

She does NOT know

```text
Voldemort's current location
```

unless canon allows it.

---

# 12. Emotion Evaluation

Emotion is recalculated before dialogue.

Inputs

```text
Recent Events

↓

Relationships

↓

Current Goal

↓

Health

↓

World State
```

Output

```text
Focused

Happy

Concerned

Angry

Confused

Fearful
```

Emotion affects tone.

Never personality.

---

# 13. Dialogue Generation

Prompt receives

```text
Identity

Speech Style

Personality

Emotion

Goal

Knowledge

Relationships

Relevant Memories

Scene

User Action
```

Produces

```text
Natural dialogue.
```

---

# 14. Internal Thoughts

Characters also produce hidden reasoning.

Example

```text
User asked about Snape.

I trust the user enough.

I'll answer honestly.

I shouldn't reveal Dumbledore's secrets.
```

Internal thoughts are

NOT shown to the user.

They help Simulation Engine.

---

# 15. Requested Actions

Characters may request actions.

Example

```text
Hermione

↓

Walk to bookshelf.
```

or

```text
Harry

↓

Give wand.
```

The Character Engine

does NOT execute actions.

Simulation Engine decides.

---

# 16. Knowledge Updates

Characters may learn.

Example

User

↓

"I'm from another universe."

↓

Hermione learns

```text
User claims to be from another universe.
```

Knowledge is stored.

---

# 17. Memory Updates

Every meaningful interaction creates memories.

Example

```text
Importance

84

Summary

User helped decode ancient rune.

Participants

User

Hermione
```

---

# 18. Forgetting

Characters should not remember everything forever.

Memory decay

```text
Low importance

↓

Gradually forgotten.
```

High importance memories remain.

---

# 19. Personality Constraints

Personality cannot change.

Hermione

will never become

reckless

without extraordinary events.

The validator rejects inconsistent outputs.

---

# 20. Speech Constraints

Speech profile controls

Vocabulary

Sentence length

Humor

Formality

Confidence

Never allow

ChatGPT style responses.

---

# 21. Validation

Validator checks

✔ Personality respected

✔ Knowledge respected

✔ Rules respected

✔ Memory consistency

✔ Speech consistency

✔ Goal consistency

Reject invalid dialogue.

---

# 22. Interaction with Other Engines

Reads

```text
Universe

World State

Relationships

Scene

Memory Store
```

Requests

```text
Simulation Engine

↓

Execute Action
```

Updates

```text
Memory Engine

↓

Save Memory
```

---

# 23. Prompt Strategy

Character Engine uses several prompts.

```text
build_character_context.txt

retrieve_memories.txt

evaluate_emotion.txt

character_dialogue.txt

update_memory.txt

update_knowledge.txt

validate_character.txt
```

Avoid one giant prompt.

Each module should be independently testable.

---

# 24. Example Flow

```text
User

↓

Ask Hermione

↓

Load Hermione

↓

Load Scene

↓

Load Memories

↓

Load Knowledge

↓

Evaluate Emotion

↓

Generate Dialogue

↓

Create New Memory

↓

Return Response
```

---

# 25. Performance Considerations

Do not load

* every character
* every memory
* every relationship
* the full universe

Only load what's relevant to the current interaction.

This keeps latency and token usage low while improving response quality.

---

# 26. Future Extensions

The engine is designed to support:

```text
Voice synthesis

Facial expressions

Internal monologue generation

Daily schedules

Conversation history summaries

Long-term memory consolidation

Belief systems

Rumor propagation

Trust networks
```

without changing the core architecture.

---

# 27. Summary

The Character Engine is the **mind** of every character in Headcanon.

It transforms structured data—identity, personality, memories, knowledge, emotions, and goals—into believable, canon-faithful behavior. Rather than acting as a generic conversational AI, it reasons from the character's perspective, ensuring that every response reflects who that character is, what they know, how they feel, and what they have experienced within the evolving universe.
