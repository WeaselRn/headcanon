# Headcanon Agent Rules

The docs folder is the single source of truth.

Never invent APIs.

Never modify docs unless instructed.

Never change storage schema.

Never remove existing functionality.

Always run linting before completion.

Always run tests.

After every milestone:

- build
- lint
- typecheck
- backend tests

If any test fails,
fix it before stopping.

Never continue to the next milestone automatically.

Wait for approval.