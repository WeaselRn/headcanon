# Retry Strategy

## Purpose

This document defines how Headcanon handles failures during prompt execution.

Since Large Language Models are probabilistic, prompts may occasionally return malformed JSON, incomplete outputs, inconsistent references, or hallucinated information.

The Retry Strategy ensures prompt reliability while preventing invalid data from entering the simulation.

---

# Design Principles

Retries should

- Preserve determinism where possible
- Minimize additional token usage
- Prevent infinite retry loops
- Never modify the World State using invalid output

Retries are a recovery mechanism, not normal execution.

---

# Failure Categories

Prompt failures include

- Invalid JSON
- Schema validation failure
- Missing required fields
- Invalid entity references
- Hallucinated entities
- World rule violations
- Context overflow
- API failures
- Rate limiting
- Timeout

Each category may require a different recovery strategy.

---

# Retry Pipeline

Prompt Execution

↓

Response Validation

↓

Success

or

Retry

↓

Validation

↓

Fallback

↓

Error

---

# Retry Levels

## Level 1

Simple Retry

Used for

- Timeout
- Temporary API failure
- Rate limiting

Re-execute the same prompt.

---

## Level 2

Corrective Retry

Used for

- Invalid JSON
- Missing fields
- Schema violations

Append validation errors to the retry context.

Example

Previous response failed because:

- Missing "character_id"
- Invalid relationship value

Please regenerate a valid response.

---

## Level 3

Reduced Context Retry

Used when

- Context length exceeded
- Token limit exceeded

Reduce

- Retrieved memories
- Event history
- Scene history

while preserving essential information.

---

## Level 4

Fallback Prompt

Use a simplified version of the prompt.

Example

Instead of

Generate dialogue and emotional updates.

Fallback

Generate dialogue only.

---

## Level 5

Abort

If retries fail

↓

Reject Output

↓

Preserve Current World State

↓

Log Failure

↓

Return Error

The simulation must never continue with invalid prompt output.

---

# Maximum Retries

Suggested limits

API Failures

3

Schema Errors

2

Context Errors

1

Validation Errors

2

After reaching the limit, execution should fail gracefully.

---

# Validation Between Retries

Every retry should repeat

- JSON Parsing
- Schema Validation
- Reference Validation
- World Rule Validation
- Business Logic Validation

Skipping validation is not permitted.

---

# Context Preservation

Retries should preserve

- Current World State
- Prompt Version
- Character Context
- Timeline State

Retries should not introduce new context unrelated to the original request.

---

# Logging

Every retry should record

- Prompt Name
- Prompt Version
- Retry Count
- Failure Reason
- Timestamp
- Execution Time

This information supports debugging and prompt improvement.

---

# Performance

Retries should

- Minimize latency
- Avoid unnecessary LLM calls
- Use cached context
- Stop immediately after successful validation

---

# Future Extensions

Potential improvements

- Model-specific retry strategies
- Automatic prompt repair
- Confidence-based retries
- Multi-model fallback
- Self-validation prompts

---

# Design Principles

The Retry Strategy should

- Maximize reliability
- Preserve consistency
- Minimize token usage
- Prevent invalid World State updates
- Remain independent of any specific LLM provider

---

# Related Documents

- 01_prompt_architecture.md
- 02_json_contracts.md
- 04_token_budget.md
- 05_prompt_versioning.md
- ../error_handling.md
- ../runtime_pipeline.md