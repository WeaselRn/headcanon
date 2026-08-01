
# Universe Builder

**Version:** 1.0

**Status:** Draft

**Owner:** Headcanon Core Engine

---

# 1. Purpose

The Universe Builder is the first intelligent component of Headcanon.

Its responsibility is **not to summarize a story**, but to reconstruct an explorable, machine-readable universe from it.

Input:

```text
Harry Potter and the Philosopher's Stone
```

Output:

```text
Universe

├── Characters
├── Locations
├── Objects
├── Timeline
├── Rules
├── Relationships
├── Knowledge Graph
└── Initial World State
```

After this stage, the original story is no longer required for interaction.

The Universe becomes the source of truth.

---

# 2. Responsibilities

The Universe Builder is responsible for:

* Cleaning imported text
* Understanding story structure
* Identifying canon
* Extracting world entities
* Building references
* Creating the initial world state
* Validating consistency
* Producing a complete Universe JSON

It is **not responsible** for:

* Character dialogue
* Simulation
* Media generation
* Timeline mutations
* User interactions

---

# 3. Inputs

Supported sources:

```text
PDF

EPUB

Plain Text

Markdown

AO3 URL

Wattpad URL

Project Gutenberg URL
```

Everything is converted into clean text before processing.

---

# 4. Outputs

Produces exactly one artifact.

```text
Universe
```

Containing

```text
Metadata

Canon

Characters

Locations

Objects

Timeline

Relationships

Rules

Knowledge Graph

World State
```

---

# 5. High-Level Pipeline

```text
Story

↓

Text Cleaning

↓

Chapter Segmentation

↓

Universe Extraction

↓

Entity Linking

↓

Relationship Building

↓

Timeline Construction

↓

World Initialization

↓

Validation

↓

Universe JSON
```

---

# 6. Internal Architecture

```text
Universe Builder

├── Text Cleaner

├── Story Segmenter

├── Character Extractor

├── Location Extractor

├── Object Extractor

├── Event Extractor

├── Rule Extractor

├── Relationship Builder

├── Graph Builder

├── World Initializer

└── Validator
```

Every module has a single responsibility.

---

# 7. Stage 1 — Text Cleaning

Input

```text
Raw extracted text
```

Removes

* page numbers
* headers
* footers
* OCR artifacts
* repeated whitespace
* broken paragraphs

Preserves

* dialogue
* chapter breaks
* scene boundaries

Output

```text
Clean Story
```

---

# 8. Stage 2 — Story Segmentation

The cleaned story is divided into logical units.

Example

```text
Chapter 1

↓

Scene 1

↓

Scene 2

↓

Scene 3
```

Segmentation allows extraction to operate on manageable context windows.

---

# 9. Stage 3 — Entity Extraction

Each segment is analyzed independently.

Extractors identify:

Characters

Locations

Objects

Events

Rules

Relationships

Each extractor returns structured JSON.

No free-form text.

---

# 10. Character Extraction

Output example

```json
{
  "id":"char_hermione",
  "name":"Hermione Granger",
  "role":"Student",
  "first_appearance":"chapter_5"
}
```

Duplicates are merged later.

---

# 11. Location Extraction

Output

```json
{
  "id":"loc_library",
  "name":"Library",
  "description":"Large magical library"
}
```

---

# 12. Object Extraction

Output

```json
{
  "id":"obj_sorting_hat",
  "name":"Sorting Hat"
}
```

---

# 13. Event Extraction

Events become the timeline.

Example

```json
{
  "id":"evt_sorting",
  "title":"Sorting Ceremony",
  "participants":[
      "char_harry",
      "char_ron"
  ]
}
```

---

# 14. Rule Extraction

Rules define immutable mechanics.

Example

```text
Only witches and wizards can naturally perform magic.
```

↓

```json
{
    "rule":"Magic requires magical ability."
}
```

---

# 15. Relationship Builder

Characters rarely state relationships explicitly.

Builder infers them.

Example

```text
Harry trusts Hermione.
```

↓

```json
{
    "source":"char_harry",
    "target":"char_hermione",
    "relationship":"Friend",
    "affinity":92
}
```

---

# 16. Knowledge Graph Builder

Produces

```text
Harry

↓

Owns

↓

Nimbus 2000

↓

Stored In

↓

Dormitory
```

Every entity becomes a node.

Every relationship becomes an edge.

---

# 17. World Initializer

Creates the starting simulation state.

Example

```text
Current Day

Characters

Locations

Inventories

Weather

Time

Active Events
```

No user interaction has occurred yet.

---

# 18. Validation

Validator checks

✔ Missing IDs

✔ Broken references

✔ Invalid locations

✔ Duplicate characters

✔ Duplicate objects

✔ Timeline ordering

✔ Graph integrity

Invalid universes are rejected.

---

# 19. Prompt Strategy

The Universe Builder should **not** rely on one giant prompt.

Instead, use specialized prompts:

```text
clean_story.txt

extract_characters.txt

extract_locations.txt

extract_objects.txt

extract_events.txt

extract_rules.txt

build_relationships.txt

build_graph.txt

initialize_world.txt
```

This modular approach improves accuracy, debuggability, and allows selective retries.

---

# 20. Storage

After validation:

```text
Universe JSON

↓

Backblaze B2

↓

universes/

↓

hp_001/

↓

universe.json
```

All later engines consume this artifact.

---

# 21. Failure Handling

If extraction fails:

* Retry only the failed module.
* Preserve successful outputs.
* Log extraction errors.
* Never regenerate the entire universe unless necessary.

This makes processing large novels more reliable.

---

# 22. Future Extensions

The builder can later support:

```text
Automatic maps

Faction extraction

Economy extraction

Magic systems

Political systems

Creature taxonomy

Language extraction

Quest extraction
```

without changing its core architecture.

---

# 23. Summary

The Universe Builder is the **compiler** of Headcanon.

It transforms an unstructured narrative into a structured, persistent universe that every other engine depends on. By decomposing extraction into specialized modules, validating cross-references, and initializing the world's starting state, it lays the foundation for consistent character interactions, world simulation, and long-term persistence. It is the single most critical engine in the Headcanon architecture.
