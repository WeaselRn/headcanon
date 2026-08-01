# Token Budget

## Purpose

This document defines how Headcanon manages Large Language Model context windows and token consumption throughout the runtime pipeline.

Since every prompt has finite context, the system must intelligently allocate tokens while preserving narrative consistency, character behavior, and world state.

Efficient token management improves latency, reduces API costs, and increases response quality.

---

# Design Principles

The token budget should

- Prioritize relevant context
- Minimize redundancy
- Reduce API cost
- Improve response speed
- Prevent context overflow

Every prompt should receive only the information required to complete its task.

---

# Context Hierarchy

When constructing prompts, context should be prioritized in the following order

1. User Request

2. Current Scene

3. Current World State

4. Character Context

5. Active Events

6. Relevant Memories

7. Relevant Timeline

8. Universe Rules

9. Knowledge Graph

Lower priority information should be removed first when approaching token limits.

---

# Context Allocation

Typical prompt context

User Input

↓

Current Scene

↓

Relevant Character

↓

Relevant Memories

↓

Current Relationships

↓

Active Events

↓

World Rules

↓

Prompt Instructions

↓

Expected JSON Schema

---

# Token Priorities

Highest Priority

- User request
- Current scene
- Character personality
- World rules

High Priority

- Recent memories
- Active relationships
- Current goals

Medium Priority

- Nearby locations
- Recent events

Low Priority

- Historical events
- Archived memories
- Unrelated entities

---

# Memory Budget

Do not load every memory.

Retrieve only

- Relevant
- Important
- Recent

Suggested limits

Maximum Memories

5–10

Maximum Events

5

Maximum Relationships

10

These values may vary depending on model context size.

---

# Scene Budget

A Scene should include

- Current narration
- Visible characters
- Visible objects
- Available actions

Do not include unrelated locations or hidden entities.

---

# Character Budget

Character prompts should include

- Personality
- Current emotion
- Current goal
- Relevant memories
- Relevant relationships

Avoid including the entire character history.

---

# Timeline Budget

Timeline context should include

- Current event
- Recent events
- Pending events

Do not include completed historical events unless directly relevant.

---

# Knowledge Graph Budget

Query only nodes related to

- Current scene
- Current interaction
- Referenced entities

Avoid loading the complete graph.

---

# Prompt Size Targets

Suggested allocation

System Prompt

20%

Runtime Context

40%

User Input

10%

Expected Output Schema

10%

Reserved Completion

20%

These percentages are guidelines and may vary by model.

---

# Context Reduction Strategy

If the context exceeds limits

Remove

↓

Archived Memories

↓

Completed Events

↓

Inactive Relationships

↓

Historical Narration

↓

Low Priority Metadata

Current Scene and World Rules should never be removed.

---

# Large Universe Strategy

For large universes

- Retrieve data on demand
- Use semantic search
- Use Knowledge Graph traversal
- Load nearby entities only

Never load the complete universe into a single prompt.

---

# Monitoring

Track

- Prompt Tokens
- Completion Tokens
- Total Tokens
- Average Tokens per Engine
- Failed Requests due to Context Limits

These metrics help optimize future prompt design.

---

# Future Extensions

Potential improvements

- Adaptive token allocation
- Model-specific budgets
- Automatic context summarization
- Hierarchical memory compression
- Dynamic retrieval strategies

---

# Design Principles

The Token Budget should

- Preserve narrative quality
- Minimize unnecessary context
- Improve performance
- Scale to large universes
- Remain independent of any specific LLM

---

# Related Documents

- 01_prompt_architecture.md
- 02_json_contracts.md
- 03_retry_strategy.md
- 05_prompt_versioning.md
- ../runtime_pipeline.md
- ../engines/02_character_engine.md