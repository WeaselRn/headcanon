# Media Gallery

## Purpose

The Media Gallery is the visual history of a universe.

Unlike a normal image gallery, every asset is connected to

- a scene
- a location
- a timeline event
- a world snapshot
- participating characters

The gallery allows users to revisit memorable moments throughout their journey.

---

# Philosophy

Media represents memories.

Every generated illustration, narration and ambient sound captures a specific
moment in the evolving universe.

The gallery should feel like browsing an album of adventures rather than a file
manager.

---

# Gallery Hierarchy

```
Universe

↓

Timeline

↓

Scene

↓

Assets
```

---

# Layout

```
┌──────────────────────────────────────────────────────────────┐
│ Media Gallery                                                │
├──────────────────────────────────────────────────────────────┤
│ Timeline │ Characters │ Locations │ Asset Types              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [Scene Image]  [Scene Image]  [Scene Image]                 │
│                                                              │
│  Breakfast      Forbidden      Library                       │
│  Great Hall     Forest         Afternoon                     │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│ Selected Asset                                               │
│                                                              │
│ Full Image                                                   │
│ Narration                                                    │
│ World State                                                  │
│ Characters                                                   │
│ Timeline                                                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

# Gallery Views

The gallery supports multiple views.

## Timeline View

Displays assets chronologically.

```
Day 1

↓

Day 2

↓

Day 3
```

---

## Character View

Displays all media involving one character.

Example

```
Hermione

↓

12 Images

↓

8 Narrations

↓

4 Audio Scenes
```

---

## Location View

Displays media grouped by location.

Example

```
Great Hall

↓

Library

↓

Forbidden Forest
```

---

## Scene View

Displays every asset belonging to one scene.

Example

```
Scene

↓

Illustration

↓

Narration

↓

Ambient Audio
```

---

# Asset Card

Each asset card displays

- thumbnail
- title
- location
- characters
- creation time

Example

```
Breakfast in the Great Hall

Characters

Harry

Hermione

Location

Great Hall

Day 2
```

---

# Asset Viewer

Selecting an asset opens

- full-resolution image
- narration playback
- ambient playback
- world information

The user should immediately understand

"What moment am I looking at?"

---

# World Context

Every asset displays

```
Current Location

↓

Current Time

↓

Characters Present

↓

Snapshot

↓

Timeline Event
```

The gallery is connected to the simulation.

---

# Timeline Jump

Every asset contains

```
Open Snapshot
```

Selecting it restores the world to that moment (read-only by default).

Example

```
Image

↓

Open Snapshot

↓

Replay Scene
```

---

# Regeneration

Users may regenerate

- illustration
- narration
- ambience

Regeneration creates a new version.

Old versions remain accessible.

---

# Version History

Every regenerated asset displays

```
Version 1

↓

Version 2

↓

Version 3
```

Users can compare versions.

---

# Search

Search supports

- character
- location
- event
- dialogue
- object
- asset type
- date

Example

```
Hermione

↓

Library

↓

Images
```

---

# Filters

Supported filters

- Images
- Narration
- Audio
- Favorites
- Latest
- Oldest

Filters may be combined.

---

# Favorites

Users may bookmark important moments.

Example

```
❤️ Saved Moments

↓

14 Assets
```

Favorites never modify the underlying universe.

---

# Sharing

Future versions may allow

- public gallery links
- snapshot sharing
- downloadable albums

Shared assets should include provenance information.

---

# Mobile Layout

On mobile

Assets appear in a vertically scrolling gallery.

The asset viewer opens fullscreen.

---

# Accessibility

Support

- keyboard navigation
- screen readers
- captions
- transcript viewing
- audio controls

---

# Future Features

The Media Gallery should support

- videos
- voice conversations
- world replays
- cinematic timelines
- multiplayer memories
- AI-generated recaps

without redesigning the interface.

---

# Design Principles

The Media Gallery should feel

- nostalgic
- cinematic
- personal
- organized

Users should experience it as a scrapbook of their journey through the universe, not as a folder of generated files.