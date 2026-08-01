# Character Panel

## Purpose

The Character Panel displays every character currently visible within the active Scene.

It acts as the user's primary gateway for interacting with NPCs and provides contextual information without exposing hidden world knowledge.

The panel reflects the current World State and updates after every simulation cycle.

---

# Responsibilities

The Character Panel is responsible for

- Displaying visible characters
- Showing character status
- Presenting interaction options
- Indicating relationship changes
- Updating dynamically as the world evolves

---

# Visibility Rules

Only characters that satisfy all visibility conditions should appear.

A character must

- Exist in the current location
- Not be hidden
- Not be removed from the scene
- Be observable by the user

Characters outside the current scene should never be displayed.

---

# Character Card

Each visible character is represented by a Character Card.

Each card contains

- Portrait
- Name
- Current Emotion
- Current Activity
- Availability Indicator
- Relationship Indicator (optional)

Example

Hermione Granger

Emotion
Focused

Activity
Reading

Available
Yes

---

# Portrait

Display

- Generated portrait
- Placeholder image
- Cached portrait

Portraits should remain consistent throughout a universe.

---

# Status Information

Display

- Current Emotion
- Current Activity
- Current Location (optional)
- Interaction Status

Example

Emotion

Curious

Activity

Examining an ancient book

---

# Interaction Options

Selecting a character opens available actions.

Examples

- Talk
- Ask
- Observe
- Give Item
- Trade
- Follow
- Inspect
- Challenge

Available actions are generated dynamically by the backend.

---

# Dialogue Entry

Users may

- Type natural language
- Select quick actions
- Ask contextual questions

Example

Ask Hermione about Snape.

The request is forwarded to the Interaction Engine.

---

# Relationship Indicator

Optionally display relationship progress.

Examples

Unknown

Neutral

Friendly

Trusted

Close

Relationship values should never expose exact internal simulation scores.

---

# Emotional Indicators

Current emotion may be represented by

- Icon
- Colour accent
- Small badge

The indicator should communicate mood without overwhelming the interface.

---

# Dynamic Updates

Refresh when

- Character enters
- Character leaves
- Emotion changes
- Activity changes
- Relationship changes
- Simulation updates

Cards should update automatically after Scene regeneration.

---

# Sorting

Default priority

1. User companions
2. Characters currently interacting
3. Important story characters
4. Other visible NPCs

Sorting should remain stable unless the scene changes significantly.

---

# Empty State

If no visible characters exist

Display

"No one else is here."

Interaction options should adjust accordingly.

---

# Performance

The panel should

- Lazy load portraits
- Cache generated assets
- Avoid unnecessary rerenders
- Update only when scene version changes

---

# Future Extensions

Potential additions

- Voice indicators
- Character health
- Companion management
- Live movement animations
- Multiplayer presence

---

# Related Documents

- 01_scene_layout.md
- 03_interaction_ui.md
- ../universe/12_scene.md
- ../engines/02_character_engine.md
- ../engines/05_scene_engine.md