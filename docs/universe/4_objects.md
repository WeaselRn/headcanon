# `docs/universe/04_objects.md`

---

# Objects

**Version:** 1.0

**Status:** Draft

**Owner:** World State Engine

---

# 1. Purpose

Objects represent every significant physical (or virtual) entity that exists within the universe and can be owned, moved, used, destroyed, created, or interacted with.

Unlike scenery, objects have persistent state.

Examples:

* Elder Wand
* Time Turner
* One Ring
* Nimbus 2000
* Marauder's Map
* Poké Ball
* Lightsaber

Objects are first-class entities within the simulation.

---

# 2. Design Philosophy

Objects should satisfy six principles.

## Persistence

Objects continue existing until destroyed.

---

## Identity

Every important object has a permanent identity.

---

## Ownership

Every object belongs somewhere.

Either

* a character
* a location
* another object

Never nowhere.

---

## State

Objects change state over time.

---

## Canon

Objects preserve canonical properties.

---

## Simulation

Objects influence future events.

---

# 3. Object Lifecycle

```text
Universe Builder

↓

Extract Objects

↓

Assign Initial Owner

↓

Assign Initial Location

↓

Simulation

↓

State Changes

↓

Transfers

↓

Snapshots
```

---

# 4. Object Schema

```json
{
    "id": "",
    "name": "",
    "aliases": [],
    "category": "",
    "description": "",
    "appearance": {},
    "properties": {},
    "owner": "",
    "location": "",
    "container": "",
    "state": {},
    "abilities": [],
    "history": [],
    "metadata": {}
}
```

---

# 5. Identity

Every object receives a permanent ID.

Example

```json
{
    "id":"obj_elder_wand",
    "name":"Elder Wand"
}
```

IDs never change.

---

# 6. Categories

Possible categories

```text
Weapon

Book

Potion

Tool

Key

Vehicle

Food

Treasure

Artifact

Clothing

Furniture

Document

Creature Item

Magic Item
```

---

# 7. Description

Canonical description.

Example

```text
An ancient wand made from elder wood,
considered the most powerful wand ever created.
```

Never changes.

---

# 8. Appearance

Visual metadata.

```json
{
    "color":"Dark Brown",

    "material":"Elder Wood",

    "size":"15 inches",

    "condition":"Pristine"
}
```

Used by Media Engine.

---

# 9. Owner

Every object has an owner.

Example

```json
{
    "owner":"char_harry"
}
```

Owner can be

Character

Location

Faction

None

---

# 10. Location

Current physical location.

Example

```json
{
    "location":"loc_headmaster_office"
}
```

Owner and location are different.

Example

Harry owns broom.

↓

Broom stored in dormitory.

---

# 11. Container

Some objects exist inside others.

Example

```text
Coin

↓

Wallet

↓

Inventory
```

Container stores nesting.

---

# 12. Properties

Immutable characteristics.

Example

```json
{
    "weight":"1 kg",

    "rarity":"Legendary",

    "material":"Silver",

    "magic":true
}
```

---

# 13. Dynamic State

State changes.

Example

```json
{
    "durability":72,

    "broken":false,

    "charged":91,

    "locked":false
}
```

Simulation updates state.

---

# 14. Abilities

Objects may enable actions.

Example

```text
Elder Wand

↓

Cast Magic

↓

Repair Wand

↓

Amplify Spells
```

---

# 15. History

Every major state change is recorded.

Example

```json
[
    {
        "event":"Created"
    },

    {
        "event":"Owned by Dumbledore"
    },

    {
        "event":"Transferred to Harry"
    }
]
```

History never disappears.

---

# 16. Ownership Transfer

Example

```text
Harry

↓

Gives Wand

↓

Hermione
```

Updates

Owner

Inventory

Relationship history

Snapshot

---

# 17. Destruction

Destroyed objects remain in history.

Example

```json
{
    "destroyed":true,

    "destroyed_by":"char_harry"
}
```

Never delete them.

---

# 18. Creation

Simulation may create objects.

Example

```text
Craft Potion

↓

New Object

↓

Inventory
```

Generated objects receive IDs.

---

# 19. Consumption

Consumables disappear after use.

Example

```text
Drink Potion

↓

Potion Removed

↓

Effects Applied
```

History remains.

---

# 20. Object Context

Character Engine receives nearby objects.

Example

```json
{
    "nearby_objects":[
        "Sorting Hat",
        "House Cup"
    ]
}
```

---

# 21. Interaction Types

Objects support

```text
Inspect

Take

Drop

Give

Use

Equip

Unequip

Open

Close

Unlock

Read

Destroy

Repair

Craft

Combine
```

Each object exposes valid actions.

---

# 22. Object Dependencies

Some objects require others.

Example

```text
Locked Door

↓

Requires

↓

Golden Key
```

Simulation validates dependencies.

---

# 23. World Updates

Object changes affect

Characters

Locations

Events

Timeline

Relationships

Example

Destroy Horcrux

↓

Timeline Changes

↓

Voldemort Weakens

---

# 24. Validation Rules

Every object must satisfy

✔ Unique ID

✔ Name exists

✔ Category exists

✔ Valid owner

✔ Valid location

✔ Valid container

✔ Valid history

✔ Valid abilities

Reject invalid objects.

---

# 25. Storage

Objects stored individually.

```text
universes/

    hp_001/

        objects/

            elder_wand.json

            sorting_hat.json

            marauders_map.json
```

---

# 26. Engine Responsibilities

Universe Builder

* Extract objects

Simulation Engine

* Update ownership
* Update state
* Handle destruction
* Handle crafting

Character Engine

* Read inventory
* Read nearby objects

Interaction Engine

* Validate actions

Storage Engine

* Persist object state

---

# 27. Future Extensions

Objects support future systems such as

```text
Economy

Crafting

Enchantments

Wear and Tear

Trading

Collections

Quest Items

Ownership Certificates

Replication

Procedural Objects
```

---

# 28. Summary

Objects are **persistent interactive entities** that bridge characters and locations. Their identity and canonical properties remain stable, while their ownership, condition, and history evolve through user actions and world simulation.

They are not merely inventory entries—they are living components of the universe whose state can influence relationships, events, and the overall progression of the world's timeline.
