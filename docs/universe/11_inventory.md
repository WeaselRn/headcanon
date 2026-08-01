# Inventory

## Purpose

The Inventory System manages the ownership, location, condition, and interaction state of all objects within the universe.

Inventories are dynamic and evolve as characters and users interact with the world.

Every item exists only once within the universe unless explicitly defined otherwise.

---

# Responsibilities

The Inventory System is responsible for

- Tracking item ownership
- Tracking item locations
- Managing item transfers
- Recording item state changes
- Supporting item interactions
- Maintaining inventory consistency

---

# Inventory Ownership

Every item belongs to exactly one of the following:

- Character
- Location
- Container
- World

An item can never exist in multiple inventories simultaneously.

---

# Inventory Structure

Each inventory contains

- Inventory ID
- Owner ID
- Inventory Type
- Capacity (optional)
- Item List

---

# Item Structure

Each item contains

- Item ID
- Name
- Description
- Category
- Current Owner
- Current Location
- Condition
- Visibility
- Quantity
- Interaction State

---

# Item Categories

Examples

- Weapon
- Tool
- Book
- Clothing
- Food
- Key Item
- Magical Artifact
- Consumable
- Quest Item
- Currency

Categories define available interactions.

---

# Item States

Possible conditions include

- New
- Good
- Worn
- Damaged
- Broken
- Destroyed

State changes should persist.

---

# Item Visibility

Items may be

- Visible
- Hidden
- Equipped
- Stored
- Locked

Visibility determines whether characters and users can interact with the item.

---

# Inventory Actions

Supported actions include

- Pick Up
- Drop
- Give
- Receive
- Equip
- Unequip
- Use
- Consume
- Destroy
- Store
- Retrieve
- Inspect

Every successful action updates the World State.

---

# Item Transfers

Transfers require

- Source inventory
- Destination inventory
- Item exists
- Item is accessible
- Capacity constraints satisfied (if applicable)

Transfer sequence

Current Owner

↓

Validation

↓

Ownership Update

↓

World State Update

↓

Snapshot

---

# Special Items

Some items influence the simulation.

Examples

- Elder Wand
- One Ring
- Death Note

Special items may

- Trigger events
- Unlock dialogue
- Modify relationships
- Enable actions
- Affect world rules

---

# Inventory Validation

The system must ensure

- No duplicate ownership
- Valid owner references
- Valid location references
- Positive quantities
- Existing items only

Invalid inventory updates are rejected.

---

# Persistence

Inventory changes are saved after

- Item transfers
- Item usage
- Equipment changes
- Simulation events
- Snapshot creation

---

# Related Documents

- 04_objects.md
- 09_world_state.md
- 10_events.md
- 15_snapshot_schema.md
- ../engines/04_simulation_engine.md