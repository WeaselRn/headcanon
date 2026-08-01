# IMPLEMENTATION.md

# Headcanon Implementation Guide

## Purpose

This document defines the implementation rules for every AI agent contributing to Headcanon.

The goal is to ensure every implementation follows the project architecture, remains consistent with the documentation, and avoids introducing technical debt.

---

# Project Philosophy

Headcanon is **not** an AI storyteller.

Headcanon is a **persistent fictional universe simulation engine**.

Never implement features that generate arbitrary stories.

Every feature should contribute to:

* Universe Reconstruction
* Persistent World State
* Character Simulation
* World Simulation
* Interactive Exploration

---

# Source of Truth

The following order of authority must always be respected.

1. `/docs`
2. `IMPLEMENTATION.md`
3. Existing schemas
4. Existing code

If the code contradicts the documentation,

**the documentation wins.**

Never silently change documentation.

---

# Before Writing Code

Always:

* Read the relevant documentation.
* Understand the engine responsibilities.
* Identify all dependencies.
* Reuse existing modules whenever possible.

Never begin implementation by guessing.

---

# Scope Rules

Implement **only** the requested milestone.

Never implement future milestones.

Never add "helpful" features.

Never refactor unrelated code.

Never rename files unless instructed.

---

# Milestone Workflow

Every implementation should follow this workflow.

1. Read relevant documentation.
2. Identify affected files.
3. Implement one feature.
4. Run formatting.
5. Run linting.
6. Run type checking.
7. Run tests.
8. Stop.
9. Wait for approval.

Never continue automatically.

---

# File Modification Rules

Modify only files required for the milestone.

Do not edit unrelated files.

Do not reorganize folders.

Do not introduce unnecessary abstractions.

Keep changes localized.

---

# Architecture Rules

Maintain strict separation of concerns.

Universe Builder

↓

World State

↓

Character Engine

↓

Interaction Engine

↓

Simulation Engine

↓

Scene Engine

↓

Media Pipeline

Never merge responsibilities.

Each engine performs exactly one job.

---

# Engine Responsibilities

Universe Builder

* Import stories
* Build Universe
* Validate Universe

Character Engine

* Generate dialogue
* Build context
* Suggest memory updates

Memory Engine

* Store memories
* Retrieve memories

Relationship Engine

* Update relationship graph

Simulation Engine

* Apply consequences
* Advance world state

Timeline Engine

* Maintain chronology

Scene Engine

* Produce current scene

Media Pipeline

* Generate images
* Generate narration
* Store media

---

# Data Model Rules

Never invent fields.

Never remove documented fields.

All models must match the schemas in `/docs/universe`.

Prefer immutable models where appropriate.

Use Pydantic v2 models.

---

# Prompt Rules

Prompts are modular.

One prompt.

One responsibility.

Never create giant prompts.

Never duplicate prompt logic.

If multiple prompts are needed,

compose them.

---

# API Rules

APIs must match `/docs/api`.

Never invent endpoints.

Never change request or response schemas without documentation updates.

Return structured JSON only.

---

# Validation Rules

Validate:

* IDs
* References
* Timeline order
* Graph integrity
* World consistency

Reject invalid universes.

Never silently repair corrupted data.

---

# World State Rules

The Universe is immutable.

The World State is mutable.

Never modify the Universe after reconstruction.

All runtime changes belong in the World State.

---

# Character Rules

Characters must:

* remain in character
* obey world rules
* remember interactions
* respect timeline knowledge

Never allow future knowledge.

Never expose internal implementation.

---

# Simulation Rules

Simulation must produce deterministic world updates.

User actions should modify:

* memories
* relationships
* world state
* timeline
* inventories

Simulation should never rewrite the original universe.

---

# Storage Rules

Backblaze B2 is the persistent storage layer.

Persist:

* Universe
* World State
* Snapshots
* Media
* Metadata
* Provenance

Never overwrite history.

Prefer versioned updates.

---

# Error Handling

Fail loudly.

Return meaningful errors.

Never hide exceptions.

Never swallow validation failures.

---

# Logging

Log:

* imports
* prompt execution
* validation
* storage
* simulation
* failures

Do not log secrets.

Do not log API keys.

---

# Code Style

Use:

* Python 3.11+
* Type hints everywhere
* Pydantic v2
* Docstrings
* Small functions
* Composition over inheritance

Avoid:

* global state
* duplicated logic
* deeply nested conditionals
* magic values

---

# Testing

Every feature requires:

* unit tests
* integration tests where applicable

Tests should cover:

* success
* failure
* edge cases

---

# Quality Gates

Before finishing any milestone:

Run:

```bash
ruff check .
ruff format .
mypy .
pytest
```

All must pass.

Do not ignore failures.

---

# AI Agent Rules

The AI agent must never:

* invent APIs
* invent schemas
* invent prompt formats
* invent storage layouts
* change documentation
* modify unrelated files
* skip validation
* ignore tests

---

# AI Agent Workflow

For every milestone:

Read documentation

↓

Implement only requested files

↓

Run quality checks

↓

Summarize changes

↓

Stop

↓

Wait for user approval

---

# Definition of Done

A milestone is complete only when:

* Documentation has been followed.
* Code compiles.
* Lint passes.
* Type checking passes.
* Tests pass.
* No unrelated files changed.
* Architecture remains consistent.

If any condition fails,

the milestone is **not complete**.

---

# Final Principle

Every line of code should strengthen the illusion that the user is exploring a living, persistent fictional universe.

If a change makes Headcanon behave more like a chatbot or story generator than a world simulation engine, it is the wrong implementation.
