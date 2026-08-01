# `docs/universe/07_world_rules.md`

---

# World Rules

**Version:** 1.0

**Status:** Draft

**Owner:** Simulation Engine

---

# 1. Purpose

World Rules define the immutable laws that govern a fictional universe.

Unlike events, characters, or relationships, **rules do not evolve**.

They define what is fundamentally possible and impossible within a universe.

Without World Rules, characters become generic AI assistants instead of inhabitants of their fictional worlds.

---

# 2. Design Philosophy

World Rules must satisfy six principles.

## Immutable

Rules never change through gameplay.

---

## Canonical

Rules originate from the original source material.

---

## Universal

Every engine consults the same rule set.

---

## Enforceable

Rules actively prevent impossible actions.

---

## Explainable

Every denied action should reference the violated rule.

---

## Extendable

New rules can be added without changing existing ones.

---

# 3. Rule Lifecycle

```text
Story Import

↓

Universe Builder

↓

Extract Canon Rules

↓

Validate

↓

Store Rule Set

↓

Simulation

↓

Rule Evaluation

↓

Action Allowed / Denied
```

---

# 4. Rule Schema

```json
{
  "id": "",
  "name": "",
  "category": "",
  "description": "",
  "priority": 0,
  "conditions": [],
  "effects": [],
  "exceptions": [],
  "metadata": {}
}
```

---

# 5. Rule Categories

Every rule belongs to one category.

```text
Physics

Magic

Technology

Combat

Movement

Social

Biology

Politics

Religion

Economy

Environment

Lore

Timeline

Inventory
```

---

# 6. Rule Priority

Rules may conflict.

Higher priority rules always win.

Example

```text
Priority 100

Death is permanent.

↓

Priority 60

Healing spell restores health.
```

Healing cannot revive someone because Rule 100 overrides it.

---

# 7. Physics Rules

Examples

```text
Gravity exists.

People cannot fly naturally.

Fire burns.

Water extinguishes fire.
```

Every universe defines its own physics.

---

# 8. Magic Rules

Example

Harry Potter

```text
Magic requires a wand.

Most spells require verbal incantations.

Patronus requires happy memories.

Avada Kedavra kills instantly.
```

Example

Avatar

```text
Only the Avatar can master all four elements.
```

---

# 9. Technology Rules

Example

Star Wars

```text
Hyperdrive enables FTL travel.

Lightsabers require kyber crystals.
```

Example

Cyberpunk

```text
Cyberware requires neural compatibility.
```

---

# 10. Combat Rules

Examples

```text
Characters cannot attack allies without reason.

Weapons determine damage.

Some enemies are immune to certain attacks.

Combat requires proximity.
```

---

# 11. Movement Rules

Examples

```text
Travel only through connected locations.

Characters cannot teleport.

Locked rooms require keys.

Flying requires a broom.
```

---

# 12. Social Rules

Examples

```text
Students obey professors.

Kings command soldiers.

Guild members follow guild laws.

Criminals are arrested.
```

These rules influence Simulation decisions.

---

# 13. Biology Rules

Examples

```text
Humans need sleep.

Elves age slowly.

Vampires cannot survive sunlight.

Robots do not eat.
```

---

# 14. Timeline Rules

Examples

```text
Past events cannot change.

Only Time Turners allow limited travel.

Dead characters remain dead.
```

Timeline rules protect consistency.

---

# 15. Inventory Rules

Examples

```text
One character cannot hold infinite objects.

Heavy objects reduce movement.

Legendary items have one owner.
```

---

# 16. Conditional Rules

Rules may activate only under certain conditions.

Example

```text
Werewolf

↓

Only transforms

↓

Full Moon
```

Stored as

```json
{
    "condition":"Full Moon",

    "effect":"Transform"
}
```

---

# 17. Exceptions

Every rule may contain exceptions.

Example

```text
Nobody may enter Hogwarts.

↓

Except

Students

Faculty

Invited Guests
```

---

# 18. Rule Evaluation

Simulation Engine checks rules before every action.

```text
User Action

↓

Action Parser

↓

Rule Engine

↓

Allowed?

↓

Simulation
```

If denied

↓

Explain why.

---

# 19. Example

User

```text
I cast Avada Kedavra without a wand.
```

Simulation

```text
Check Rule

↓

Magic requires wand

↓

Violation

↓

Reject action
```

---

# 20. Rule Violations

Simulation never ignores rules.

Instead

```text
Action

↓

Rejected

↓

Reason Returned
```

Example

```text
"You cannot perform this spell without a wand."
```

---

# 21. Rule Composition

Complex actions evaluate multiple rules.

Example

```text
Travel

↓

Movement Rules

↓

Inventory Rules

↓

Timeline Rules

↓

Character Status

↓

Execute
```

---

# 22. Rule References

Characters reference rules.

Objects reference rules.

Locations reference rules.

Events reference rules.

Never duplicate rule definitions.

---

# 23. Rule Inheritance

Global Rules

↓

Location Rules

↓

Object Rules

↓

Character Rules

Higher-level rules propagate downward.

Example

```text
Magic

↓

Forbidden Forest

↓

Dark Magic Allowed
```

Only affects that location.

---

# 24. Validation Rules

Every rule must satisfy

✔ Unique ID

✔ Category exists

✔ Priority defined

✔ Conditions valid

✔ Effects valid

✔ No cyclic dependencies

Reject invalid rule sets.

---

# 25. Storage

```text
universes/

    hp_001/

        rules/

            physics.json

            magic.json

            combat.json

            movement.json

            social.json
```

Rule files rarely change after creation.

---

# 26. Engine Responsibilities

Universe Builder

* Extract rules
* Categorize
* Assign priorities

Rule Engine

* Evaluate actions
* Resolve conflicts

Simulation Engine

* Apply rule outcomes

Interaction Engine

* Display explanations

Storage Engine

* Persist immutable rule set

---

# 27. Future Extensions

The rule engine supports

```text
Dynamic rule packs

Difficulty modifiers

House rules

Modded universes

Custom universes

Plugin systems

Cross-universe compatibility

Rule scripting
```

These additions extend the rule system without modifying the canonical rules.

---

# 28. Example Rule Set

```text
Rule 1

Magic requires a wand.

Priority: 100

↓

Rule 2

Expelliarmus disarms target.

Priority: 80

↓

Rule 3

Disarmed characters cannot cast spells.

Priority: 90
```

Simulation

```text
Harry casts Expelliarmus.

↓

Draco loses wand.

↓

Draco cannot cast spells.

↓

Simulation remains consistent.
```

---

# 29. Rule Extraction

Universe Builder should extract rules from implicit and explicit story content.

Example

Story

```text
Only elves may enter the sacred grove.
```

Extracted Rule

```json
{
    "category":"Movement",

    "condition":"Character is Elf",

    "effect":"Allow Entry"
}
```

Many rules are never explicitly stated but can be inferred from repeated events.

---

# 30. Summary

World Rules are the **constitution of the universe**.

They define the immutable laws governing physics, magic, technology, movement, society, biology, and chronology. Every action proposed by the user or generated by the Simulation Engine is validated against these rules before execution. This guarantees that Headcanon remains faithful to the source material, allowing the universe to evolve through user choices while never violating its own internal logic.
