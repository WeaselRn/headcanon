# Prompt Architecture

## Purpose

This document defines the prompt architecture used throughout Headcanon.

Rather than relying on a single large prompt, Headcanon uses a collection of specialized prompts, each responsible for a specific task within the universe simulation pipeline.

This modular architecture improves consistency, maintainability, scalability, and debugging.

---

# Design Philosophy

Prompts should

- Have a single responsibility
- Produce structured output
- Be deterministic where possible
- Be reusable
- Be independently versioned

No prompt should perform multiple unrelated tasks.

---

# Prompt Hierarchy

Story Import

↓

Universe Reconstruction

↓

World Initialization

↓

Character Reasoning

↓

Interaction

↓

Simulation

↓

Scene Generation

↓

Media Generation

Each stage consists of multiple specialized prompts.

---

# Prompt Categories

## Import

Responsible for

- Story cleaning
- Chapter extraction
- Metadata extraction

Location

backend/app/prompts/import/

---

## Universe

Responsible for

- Character extraction
- Location extraction
- Timeline extraction
- Rule extraction
- Knowledge graph generation

Location

backend/app/prompts/universe/

---

## Character

Responsible for

- Dialogue
- Personality consistency
- Memory updates
- Relationship updates
- Emotional updates

Location

backend/app/prompts/characters/

---

## Interaction

Responsible for

- Parsing user intent
- Validating actions
- Selecting interaction strategies

Location

backend/app/prompts/interaction/

---

## Simulation

Responsible for

- World simulation
- Event generation
- Timeline updates
- Conflict resolution

Location

backend/app/prompts/simulation/

---

## Scene

Responsible for

- Scene generation
- Narration
- Action generation

Location

backend/app/prompts/scene/

---

## Media

Responsible for

- Image prompts
- Narration prompts
- Ambient audio prompts

Location

backend/app/prompts/media/

---

# Prompt Lifecycle

Load Prompt

↓

Inject Runtime Context

↓

Call LLM

↓

Validate Output

↓

Parse JSON

↓

Return Structured Data

No prompt output should bypass validation.

---

# Prompt Inputs

A prompt may receive

- World State
- Character Context
- Timeline
- Scene Context
- User Action
- Universe Rules
- Relevant Memories

Each prompt should receive only the minimum required context.

---

# Prompt Outputs

Prompts should return

- Structured JSON
- Deterministic fields
- Machine-readable values

Avoid free-form responses unless specifically required.

---

# Context Injection

Context should be assembled by dedicated engines.

Examples

Character Engine

↓

Personality

Relevant Memories

Current Emotion

Relationships

↓

Dialogue Prompt

Prompts should never retrieve data themselves.

---

# Prompt Independence

Each prompt should

- Operate independently
- Be testable
- Be replaceable
- Be reusable

Changing one prompt should not require modifying unrelated prompts.

---

# Prompt Versioning

Every prompt should include

- Prompt Name
- Prompt Version
- Last Modified
- Compatible Schema Version

Prompt versions should be tracked separately from engine versions.

---

# Error Handling

If a prompt fails

↓

Retry

↓

Validate

↓

Fallback

↓

Report Error

The World State must never be updated using invalid prompt output.

---

# Performance

Prompt execution should

- Minimize token usage
- Reuse cached context
- Avoid duplicated information
- Execute only when required

---

# Future Extensions

Potential improvements

- Model-specific prompt optimization
- Dynamic prompt routing
- Multi-model orchestration
- Prompt benchmarking
- Automatic prompt evaluation

---

# Related Documents

- 02_json_contracts.md
- 03_retry_strategy.md
- 04_token_budget.md
- 05_prompt_versioning.md
- ../runtime_pipeline.md
- ../engines/