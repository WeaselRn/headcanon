# JSON Contracts

## Purpose

This document defines the JSON output contracts used by every LLM prompt within Headcanon.

Every prompt must produce predictable, machine-readable JSON that can be validated before entering the simulation pipeline.

LLM output should never directly modify the World State.

All outputs must first pass schema validation.

---

# Design Principles

Prompt outputs should

- Be valid JSON
- Follow predefined schemas
- Contain deterministic field names
- Avoid unnecessary text
- Avoid Markdown
- Avoid explanations unless explicitly requested

The backend should never parse natural language when structured JSON is expected.

---

# Validation Pipeline

LLM Response

↓

JSON Parsing

↓

Schema Validation

↓

Reference Validation

↓

Business Validation

↓

Accepted Output

Invalid responses must never update the World State.

---

# Required Properties

Every JSON response should contain

- schema_version
- prompt_version
- timestamp (optional)
- payload

Example

{
    "schema_version": "1.0",
    "prompt_version": "2.1",
    "payload": {}
}

---

# Primitive Types

Supported data types

- String
- Integer
- Float
- Boolean
- Array
- Object
- Null (only when explicitly allowed)

---

# Entity References

Objects should reference existing entities using IDs.

Correct

{
    "character_id": "char_001"
}

Incorrect

{
    "character": "Hermione"
}

IDs should remain stable across the universe.

---

# Enumerations

Where possible, use fixed values.

Example

Emotion

- Happy
- Sad
- Angry
- Curious
- Fearful

Avoid generating new enum values unless supported by the schema.

---

# Arrays

Arrays should

- Preserve ordering where required
- Avoid duplicates
- Contain valid object types

Empty arrays are preferred over null.

---

# Optional Fields

Optional properties should be omitted unless they contain meaningful data.

Avoid placeholder values.

---

# Numeric Constraints

Examples

Relationship Score

0–100

Importance

0–100

Emotion Intensity

0–100

Values outside accepted ranges should fail validation.

---

# Object References

Before acceptance

Verify

- Character IDs exist
- Location IDs exist
- Object IDs exist
- Event IDs exist

Broken references invalidate the response.

---

# Unknown Fields

Unexpected fields should

- Be ignored during development (optional)
- Trigger warnings
- Be rejected in production

Schemas should remain strict.

---

# Error Handling

If validation fails

↓

Retry Prompt

↓

Revalidate

↓

Fallback

↓

Report Failure

Malformed JSON should never reach simulation.

---

# Schema Evolution

Every schema should include

- Schema Version
- Compatible Engine Version
- Prompt Version

Breaking schema changes require version increments.

---

# Example Output

{
    "schema_version": "1.0",
    "prompt_version": "1.3",
    "payload": {
        "characters": [],
        "locations": [],
        "events": []
    }
}

---

# Design Principles

The JSON Contract should

- Be deterministic
- Be versioned
- Be extensible
- Be machine-readable
- Be independent of the underlying LLM

---

# Related Documents

- 01_prompt_architecture.md
- 03_retry_strategy.md
- 05_prompt_versioning.md
- ../universe/01_universe_schema.md
- ../runtime_pipeline.md