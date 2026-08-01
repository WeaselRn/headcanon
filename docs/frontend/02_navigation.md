# World Navigation

## Purpose

Navigation in Headcanon is world navigation, not page navigation.

Users do not "open" locations.

Users travel through the universe.

Every movement changes the current world context.

Navigation should feel similar to exploring an RPG rather than browsing a website.

---

# Philosophy

The world exists independently of the player.

Moving to another location changes

- visible characters
- available actions
- active events
- narration
- atmosphere
- generated media

The world does not pause while the player moves.

---

# Navigation Hierarchy

```
Universe

↓

Region

↓

Location

↓

Scene

↓

Interaction
```

---

# Example

```
Wizarding World

↓

Hogwarts

↓

Great Hall

↓

Morning Breakfast

↓

Talk to Hermione
```

---

# Location Graph

Locations are connected as a graph.

Example

```
Great Hall

↓

Entrance Hall

↓

Library

↓

Hospital Wing

↓

Forbidden Forest
```

Movement is only allowed through valid connections.

---

# Fast Travel

Some locations support fast travel.

Example

```
Map

↓

Select Hogsmeade

↓

Travel

↓

Arrival Scene
```

Fast travel should only be available after the location has been discovered.

---

# Unknown Locations

Undiscovered places remain hidden.

Example

```
Known

✓ Great Hall

✓ Library

✓ Common Room

Hidden

?

?

?
```

Exploration unlocks new locations.

---

# World Map

The World Map displays

- discovered locations
- current location
- travel routes
- locked areas

The map is optional.

Stories without meaningful geography may hide it.

---

# Character Presence

Characters only appear where they actually are.

Example

```
Great Hall

Harry

Hermione

Ron
```

Library

```
Hermione

Madam Pince
```

Characters are not globally accessible.

---

# Arrival

Entering a location always triggers

```
Travel

↓

Simulation Update

↓

Scene Generation

↓

Narration

↓

Interaction
```

This creates the feeling of entering a living place.

---

# Travel Cost

Travel may advance

- time
- weather
- NPC schedules
- world events

Example

```
Travel to Library

↓

15 minutes pass

↓

Students leave Great Hall

↓

Library becomes crowded
```

Movement affects the simulation.

---

# Locked Locations

Some locations require

- story progression
- discovered information
- inventory items
- relationships

Example

```
Chamber of Secrets

Status

Locked

Requirement

Learn Parseltongue
```

---

# Breadcrumbs

The interface should always display

```
Wizarding World

>

Hogwarts

>

Great Hall
```

This provides context.

---

# Current Location Card

The current location displays

- illustration
- name
- atmosphere
- weather
- occupants
- connected locations

Example

```
Great Hall

Morning

Sunny

Characters

Harry

Hermione

Ron

Connected

Library

Entrance Hall

Courtyard
```

---

# Connected Locations

Only adjacent locations should be shown.

Example

```
Go to

Library

↓

Courtyard

↓

Entrance Hall
```

Not

```
Forbidden Forest
```

unless directly connected.

---

# Navigation History

The engine remembers recently visited locations.

Example

```
Great Hall

↓

Library

↓

Common Room

↓

Library
```

This enables quick backtracking.

---

# Mobile Navigation

On mobile

Navigation appears as

```
Current Location

↓

Connected Locations

↓

World Map Button
```

instead of a large sidebar.

---

# Accessibility

Navigation should support

- keyboard shortcuts
- controller support
- screen readers
- touch devices

---

# Design Principles

Navigation should feel

- natural
- immersive
- geographical
- contextual

The user should always feel like they are travelling through a real world rather than clicking between web pages.