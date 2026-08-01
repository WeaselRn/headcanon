# Error Handling

## Purpose

This document defines the error handling strategy across the Headcanon platform.

Errors should be:

- Predictable
- Recoverable where possible
- Logged
- User-friendly
- Never leave the world state in an inconsistent state

---

# Error Categories

## Validation Errors

Occurs when:

- Invalid request
- Missing required fields
- Invalid IDs
- Unsupported file format

Action

- Reject request
- Return validation error
- Do not modify world state

---

## Import Errors

Occurs during:

- PDF parsing
- EPUB parsing
- URL fetching
- Text extraction

Action

- Retry if transient
- Return import error
- Preserve uploaded file for debugging

---

## Universe Builder Errors

Occurs when:

- LLM returns malformed JSON
- Missing entities
- Invalid references
- Duplicate IDs

Action

- Attempt validation
- Retry reconstruction
- Abort if still invalid

Universe should never be partially created.

---

## Character Engine Errors

Occurs when:

- Character not found
- Missing memories
- Invalid context
- Prompt failure

Action

- Reload character
- Retry prompt
- Return graceful failure

---

## Simulation Errors

Occurs when:

- Impossible action
- Rule violation
- Timeline conflict
- Invalid world transition

Action

Reject action.

World State must remain unchanged.

---

## Storage Errors

Occurs when:

- Backblaze unavailable
- Upload failure
- Download failure
- Snapshot failure

Action

Retry uploads.

If unsuccessful:

- Preserve in memory
- Queue for retry
- Notify user

---

## Media Errors

Occurs during:

- Image generation
- Narration
- Audio generation

Action

Media generation should fail independently.

Universe progression must continue.

---

## Network Errors

Occurs when:

- Gemini timeout
- API unavailable
- Storage timeout

Retry policy

Attempt 1

↓

Attempt 2

↓

Attempt 3

↓

Fail gracefully

Use exponential backoff.

---

## Snapshot Failures

If saving fails:

- Keep world state in memory
- Retry automatically
- Never discard progress

---

## Logging

Every error should include:

- Timestamp
- Universe ID
- User ID (if applicable)
- Engine
- Error Type
- Stack Trace
- Recovery Action

---

## User Messages

Expose only user-friendly messages.

Never expose:

- Stack traces
- Prompt contents
- Internal implementation
- API keys
- Storage paths

---

# Error Severity

Critical

- World corruption
- Snapshot corruption
- Storage corruption

Major

- Simulation failure
- Universe reconstruction failure

Minor

- Media generation failure
- Missing optional asset

Info

- Retry succeeded
- Validation warning

---

# Recovery Principles

- Never corrupt the world state
- Never partially update a universe
- Prefer retry over failure
- Prefer rollback over inconsistent state
- Media failures must never block gameplay

---

# Related Documents

- runtime_pipeline.md
- deployment.md
- storage/02_storage_schema.md
- engines/04_simulation_engine.md
- engines/10_media_pipeline.md