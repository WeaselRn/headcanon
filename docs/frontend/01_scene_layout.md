# Scene Layout

## Purpose

The Scene Layout defines the primary user experience of Headcanon.

Unlike traditional AI chat applications, Headcanon is not conversation-first.

The user exists inside a living fictional universe.

The interface should always present the current world before the conversation.

The scene is the primary unit of interaction.

---

# Philosophy

Users should feel like they have entered a world.

The interface should resemble

- visual novels
- RPG exploration
- point-and-click adventures

rather than

- ChatGPT
- Discord
- messaging applications

Conversation is only one possible action.

---

# Screen Hierarchy

```
Universe

↓

Location

↓

Scene

↓

Interaction

↓

World Update
```

The scene is the center of the interface.

---

# Primary Layout

```
┌────────────────────────────────────────────────────────────┐
│ Universe                    Time              Settings     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                  Scene Illustration                        │
│                                                            │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ Narration                                                  │
│                                                            │
│ Morning sunlight pours through the enchanted ceiling...    │
│                                                            │
├───────────────┬────────────────────────────────────────────┤
│ Characters    │ Available Actions                          │
│               │                                            │
│ Harry         │ • Talk                                     │
│ Hermione      │ • Observe                                  │
│ Ron           │ • Travel                                   │
│               │ • Inspect                                  │
│               │ • Inventory                                │
├───────────────┴────────────────────────────────────────────┤
│                                                            │
│ > Ask Hermione about Snape...                              │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

# Main Sections

Every scene consists of

1. Header
2. Scene Illustration
3. Narration
4. Character Panel
5. Action Panel
6. Interaction Input

No section should dominate the interface.

---

# Header

Displays

- Universe Name
- Current Location
- Current Time
- Active Branch
- Save Status

Example

```
Harry Potter

Great Hall

Day 3

Morning

Saved
```

---

# Scene Illustration

The illustration is the visual anchor.

It represents the current scene.

It updates only when

- entering a new location
- major world changes
- explicit regeneration

It should not regenerate after every message.

---

# Narration

Narration describes the current world.

It answers

- What happened?
- Where am I?
- What is everyone doing?
- What changed?

Narration should never become a chat history.

Only the latest scene description is shown.

---

# Character Panel

Shows all visible characters.

Each card displays

- portrait
- name
- mood
- relationship indicator

Example

```
Hermione

😊 Curious

Relationship

82
```

Characters not present in the location are not shown.

---

# Action Panel

Actions are context-sensitive.

Examples

```
Talk

Observe

Travel

Inspect

Wait

Inventory
```

Additional actions may appear depending on the scene.

---

# Interaction Input

The input box accepts natural language.

Examples

```
Ask Hermione about Horcruxes.

Sit beside Harry.

Look around.

Open the chest.

Read the letter.

Go outside.

```

The user should never need to learn commands.

---

# World Update

After every interaction

The UI updates

```
Scene

↓

Narration

↓

Character States

↓

Relationships

↓

Available Actions
```

The interface should always reflect the current world state.

---

# Empty State

Before a universe is loaded

Display

```
Import Story

↓

Universe Reconstruction

↓

Enter World
```

No chat interface should be visible.

---

# Mobile Layout

On smaller screens

```
Illustration

↓

Narration

↓

Characters

↓

Actions

↓

Input
```

Characters become horizontally scrollable.

---

# Accessibility

The interface should support

- keyboard navigation
- screen readers
- high contrast mode
- reduced motion
- narration playback

---

# Design Principles

The Scene Layout should always feel

- immersive
- calm
- cinematic
- readable
- exploration-first

The user should feel like they are standing inside a fictional world, not chatting with an AI.