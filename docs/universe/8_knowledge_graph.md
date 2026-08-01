# `docs/universe/08_knowledge_graph.md`

---

# Knowledge Graph

**Version:** 1.0

**Status:** Draft

**Owner:** Universe Builder / Character Engine / Simulation Engine

---

# 1. Purpose

The Knowledge Graph is the semantic backbone of the universe.

While the Timeline answers **"What happened?"**, and the World State answers **"What exists now?"**, the Knowledge Graph answers:

* Who knows whom?
* Where is this object?
* Who owns this item?
* Which locations are connected?
* What relationships exist?
* Which events affected this character?
* How is everything connected?

It enables **reasoning instead of searching**.

---

# 2. Design Philosophy

The Knowledge Graph follows six principles.

## Universal

Everything becomes a node.

---

## Connected

Everything is connected through relationships.

---

## Queryable

Every engine can traverse the graph.

---

## Dynamic

Edges update as the universe evolves.

---

## Canonical

Initial graph comes from Universe Builder.

---

## Explainable

Every connection has a source.

---

# 3. Graph Lifecycle

```text
Story Import

↓

Universe Builder

↓

Extract Entities

↓

Extract Relationships

↓

Build Graph

↓

Persist Graph

↓

Simulation

↓

Graph Updates

↓

Save Snapshot
```

---

# 4. Graph Structure

The graph consists of

```text
Nodes

↓

Edges
```

Everything else derives from these two concepts.

---

# 5. Node Types

Every important entity becomes a node.

```text
Character

Location

Object

Event

Rule

Faction

Species

Organization

Quest

User
```

Future types may be added.

---

# 6. Edge Types

Relationships between nodes.

```text
Lives In

Owns

Knows

Visited

Uses

Created

Destroyed

Friend Of

Enemy Of

Member Of

Located In

Occurred At

Requires

Caused

Affected
```

Edges are directional.

---

# 7. Graph Schema

```json
{
  "nodes": [],
  "edges": [],
  "metadata": {}
}
```

---

# 8. Node Schema

```json
{
  "id": "",
  "type": "",
  "name": "",
  "properties": {}
}
```

Example

```json
{
    "id":"char_harry",

    "type":"Character",

    "name":"Harry Potter"
}
```

---

# 9. Edge Schema

```json
{
  "source": "",
  "target": "",
  "relationship": "",
  "weight": 1.0,
  "properties": {}
}
```

Example

```json
{
    "source":"char_harry",

    "target":"obj_nimbus",

    "relationship":"Owns"
}
```

---

# 10. Graph Example

```text
Harry

│

├── Friend Of → Hermione

├── Owns → Nimbus 2000

├── Lives In → Gryffindor Tower

└── Participated In → Troll Attack
```

---

# 11. Character Connections

Character nodes connect to

```text
Locations

Objects

Events

Relationships

Goals

Memories

Factions
```

---

# 12. Location Connections

Locations connect to

```text
Characters

Objects

Events

Connected Locations
```

Example

```text
Great Hall

↓

Connected To

↓

Entrance Hall
```

---

# 13. Object Connections

Objects connect to

```text
Owner

Location

Creator

Events

Rules
```

Example

```text
Elder Wand

↓

Owned By

↓

Harry
```

---

# 14. Event Connections

Events connect to

```text
Participants

Locations

Objects

Consequences

Previous Events

Future Events
```

Example

```text
Sorting Ceremony

↓

Occurred At

↓

Great Hall
```

---

# 15. Rule Connections

Rules connect to

```text
Characters

Objects

Locations

Events

Abilities
```

Example

```text
Magic Requires Wand

↓

Applies To

↓

Spell Casting
```

---

# 16. Dynamic Edges

Simulation updates edges.

Example

Initial

```text
Harry

↓

Owns

↓

Marauder's Map
```

User

```text
Give map to Hermione.
```

Updated

```text
Harry

↓

Previously Owned

↓

Map

↓

Now Owned By

↓

Hermione
```

---

# 17. Weighted Relationships

Some edges carry weights.

Example

```text
Trust

0.82
```

or

```text
Visited

15 times
```

Weights support reasoning.

---

# 18. Temporal Edges

Edges may have timestamps.

Example

```text
Harry

↓

Visited

↓

Forbidden Forest

↓

Day 42
```

Useful for replay.

---

# 19. Graph Queries

The graph should answer

```text
Who owns this?

↓

Where is this?

↓

Who knows this character?

↓

Which events involve Hermione?

↓

Which locations contain magical objects?

↓

Who has visited Azkaban?
```

Without scanning every object.

---

# 20. Reasoning

Knowledge Graph enables inference.

Example

```text
Harry

↓

Owns Wand

↓

Wand Required

↓

Harry

↓

Can Cast Magic
```

This inference is impossible with flat JSON alone.

---

# 21. Character Knowledge

Each character has a subgraph.

Example

```text
Hermione

↓

Knows

↓

Harry

↓

Knows

↓

Library

↓

Knows

↓

Polyjuice Potion
```

Characters never access the full graph.

Only their reachable knowledge.

---

# 22. User Node

The player is another node.

Example

```text
User

↓

Friend Of

↓

Hermione
```

No special treatment.

---

# 23. Event Reasoning

Simulation traverses the graph.

Example

```text
Ron

↓

Friend Of

↓

Harry

↓

Harry Injured

↓

Ron Visits Hospital
```

No hardcoded logic required.

---

# 24. Pathfinding

Graph traversal enables reasoning.

Example

```text
Find

Harry

↓

Friend

↓

Friend

↓

Character
```

or

```text
Shortest path

Harry

↓

Voldemort
```

Useful for relationship explanations.

---

# 25. Scene Generation

Scene Engine queries graph.

Example

```text
Current Location

↓

Characters

↓

Nearby Objects

↓

Active Events

↓

Generate Scene
```

Much faster than searching every collection.

---

# 26. Graph Updates

Simulation updates graph after

```text
Travel

Combat

Conversation

Friendship

Death

Inventory

Discovery

Quest

World Event
```

---

# 27. Validation Rules

Every graph must satisfy

✔ Unique node IDs

✔ Valid edge references

✔ No dangling nodes

✔ Valid edge types

✔ Valid node types

✔ No duplicate edges

✔ Directed edges only

Reject invalid graphs.

---

# 28. Storage

```text
universes/

    hp_001/

        graph/

            nodes.json

            edges.json
```

Large universes

```text
nodes/

edges/

indexes/
```

---

# 29. Engine Responsibilities

Universe Builder

* Extract entities
* Build initial graph

Character Engine

* Query reachable knowledge
* Build character context

Simulation Engine

* Add edges
* Remove edges
* Update weights

Interaction Engine

* Query graph

Media Engine

* Retrieve scene context

Storage Engine

* Persist graph snapshots

---

# 30. Graph Indexes

To support fast lookups, maintain indexes by

```text
Node ID

Node Type

Relationship Type

Location

Character

Object

Event

Timestamp
```

Indexes should be updated whenever the graph changes.

---

# 31. Future Extensions

The graph is designed to support advanced AI features.

```text
Vector search

Semantic retrieval

Agent planning

Quest generation

Relationship prediction

Social network analysis

Faction influence

Economic simulation

Cross-universe linking

Graph embeddings

LLM-assisted graph reasoning
```

These can be layered onto the existing graph without changing its core structure.

---

# 32. Relationship to Other Systems

The Knowledge Graph is **not a replacement** for the other universe components.

```text
Universe

├── Characters
├── Locations
├── Objects
├── Timeline
├── Relationships
├── World Rules
└── Knowledge Graph
```

The graph **references** these systems instead of duplicating them.

* **Characters** store character data.
* **Relationships** store social scores.
* **Timeline** stores chronological history.
* **Knowledge Graph** stores semantic connections between all entities.

This separation prevents duplication while allowing efficient reasoning.

---

# 33. Summary

The Knowledge Graph is the **semantic nervous system** of Headcanon.

Instead of searching independent JSON files, every engine can traverse a connected graph of characters, locations, objects, events, and rules to answer complex questions, infer new information, and simulate believable consequences. By representing the universe as interconnected knowledge rather than isolated records, Headcanon gains the ability to reason about the fictional world in a scalable and extensible way, forming the foundation for intelligent interactions, world simulation, and future AI capabilities.

