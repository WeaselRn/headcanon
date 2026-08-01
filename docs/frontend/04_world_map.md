# World Map

## Purpose

The World Map provides a visual representation of the reconstructed universe.

It allows users to

- understand the world
- explore locations
- discover hidden places
- visualize relationships between regions
- navigate naturally

The World Map is not required for every universe.

Small stories may omit it entirely.

---

# Philosophy

The map should represent the fictional world rather than a literal geographic map.

For example

Harry Potter

```
England

↓

Hogwarts

↓

Castle

↓

Great Hall
```

A visual novel may instead use

```
Town

↓

School

↓

Classroom
```

while a spaceship story may use

```
USS Enterprise

↓

Deck 1

↓

Bridge
```

The map adapts to the universe.

---

# Hierarchy

The World Map follows

```
Universe

↓

Region

↓

Sub-region

↓

Location
```

Example

```
Wizarding World

↓

Hogwarts

↓

Castle

↓

Library
```

---

# Map Structure

Each location contains

- unique ID
- display name
- parent region
- connected locations
- discovered state
- illustration
- coordinates (optional)

Example

```json
{
  "id": "great_hall",

  "name": "Great Hall",

  "parent": "hogwarts",

  "connected": [
    "entrance_hall",
    "courtyard"
  ],

  "discovered": true
}
```

---

# Discovered Locations

Locations begin in one of three states.

```
Unknown

↓

Discovered

↓

Visited
```

Unknown locations

- hidden
- unnamed
- unavailable

---

# Current Position

The player's current position should always be highlighted.

Example

```
📍 Great Hall
```

Only one current location exists.

---

# Travel

Clicking a connected location initiates travel.

```
Current Location

↓

Selected Destination

↓

Simulation

↓

Arrival Scene
```

Travel is not instantaneous.

---

# Locked Areas

Locked locations appear with a visual indicator.

Example

```
🚫 Chamber of Secrets

Requirement

Learn Parseltongue
```

The UI should explain why travel is impossible.

---

# Dynamic Locations

Locations may appear or disappear during gameplay.

Examples

- Hidden Chamber
- Secret Passage
- Temporary Camp
- Battle Arena

The map updates automatically.

---

# Region Overview

Selecting a region displays

- description
- discovered locations
- major characters
- active events

Example

```
Hogwarts

Characters

Harry

Hermione

Dumbledore

Locations

Library

Great Hall

Hospital Wing
```

---

# Character Tracking

The map may display important characters.

Example

```
Harry

📍 Gryffindor Tower

Hermione

📍 Library
```

Only if the player knows their location.

Hidden characters remain hidden.

---

# Event Markers

Major world events appear on the map.

Examples

```
⚠ Troll Attack

⭐ Main Quest

❓ Rumor

🔥 Fire
```

Markers disappear after completion.

---

# Search

The map supports searching by

- location
- character
- object
- event

Search only includes discovered content.

---

# Zoom Levels

The map supports multiple zoom levels.

```
Universe

↓

Region

↓

Location

↓

Scene
```

Users can smoothly navigate between scales.

---

# Mobile Layout

On mobile

The map opens as a full-screen overlay.

Large touch targets should be used.

---

# Accessibility

Support

- keyboard navigation
- zoom controls
- screen readers
- high contrast mode

---

# Performance

Maps should load incrementally.

Only nearby regions should be rendered initially.

Large universes should support lazy loading.

---

# Future Features

The World Map should support

- multiplayer markers
- live NPC movement
- fog of war
- minimap
- quest overlays
- custom pins

without redesigning the interface.

---

# Design Principles

The World Map should feel

- alive
- explorable
- informative
- immersive

The player should feel like they are navigating a real fictional world rather than browsing a menu.