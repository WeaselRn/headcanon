# Interaction UI

## Purpose

The Interaction UI is the primary way users influence the universe.

Unlike traditional chatbots, Headcanon interactions are world actions.

Every interaction should have consequences.

The UI should encourage exploration rather than conversation.

---

# Core Loop

The interaction loop is

```
Observe Scene

↓

Choose Action

↓

AI Processes Action

↓

Simulation Updates World

↓

Scene Refreshes

↓

Continue Exploring
```

Every interaction changes the universe.

---

# Interaction Types

Users can perform actions including

- Talk
- Observe
- Inspect
- Travel
- Use Item
- Give Item
- Pick Up
- Read
- Wait
- Follow Character
- Attack
- Cast Spell
- Custom Action

The engine should support arbitrary natural language.

---

# Natural Language

Users are never restricted to buttons.

Buttons are suggestions.

Example

```
Ask Hermione about Snape.

Sit beside Harry.

Hide under the table.

Look through the window.

Knock on the door.

Cast Lumos.

Take the diary.
```

The Interaction Engine determines intent.

---

# Suggested Actions

Each scene displays context-aware actions.

Example

```
Talk

Observe

Travel

Inspect

Inventory
```

Suggestions update dynamically.

---

# Action Categories

Actions belong to categories

```
Conversation

Movement

Investigation

Inventory

Combat

Magic

Social

Environment
```

The UI groups similar actions.

---

# Input Box

The interaction box should remain simple.

```
────────────────────────

What do you do?

> Ask Hermione about Horcruxes.

────────────────────────
```

No slash commands.

No markdown.

No roleplay syntax.

Natural language only.

---

# Processing State

While an interaction is executing

Display

```
Thinking...

Hermione considers your question...

The world is changing...
```

Avoid generic loading spinners.

The feedback should remain immersive.

---

# Interaction Result

Every interaction returns

```
Narration

↓

Character Response

↓

World Changes

↓

Available Actions
```

Example

```
Hermione lowers her voice.

"I don't think we're ready to discuss Horcruxes."

Relationship

+3

Time

Morning → Afternoon

New Action

Visit Library
```

---

# World Changes

After every interaction

The UI should clearly communicate

- relationship changes
- inventory changes
- location changes
- time changes
- quest updates
- new discoveries

Example

```
Relationship

Hermione

+2

Inventory

Old Key

Obtained

Location

Library

Unlocked
```

---

# Character Responses

Responses should appear separately from narration.

Example

```
Narration

The Great Hall grows quieter.

──────────────

Hermione

"I'm not sure that's wise."

──────────────
```

The distinction improves immersion.

---

# Consequence Indicators

Important actions display

```
This may permanently change the timeline.
```

Only when appropriate.

Minor interactions should not show warnings.

---

# Inventory Access

Inventory opens in a side panel.

```
Inventory

Wand

Marauder's Map

Chocolate Frog

Potion
```

Dragging an item onto a character or object triggers an interaction.

---

# Context Menus

Clicking an object displays

```
Inspect

Use

Take

Read

Destroy
```

Only actions valid for that object appear.

---

# Keyboard Shortcuts

Suggested shortcuts

```
Enter

Submit Action

Esc

Close Panel

Tab

Cycle Suggestions

Arrow Keys

Navigate Suggestions
```

---

# Mobile Interaction

On mobile

```
Scene

↓

Narration

↓

Quick Actions

↓

Input

↓

Keyboard
```

Quick actions become swipeable chips.

---

# Accessibility

Support

- screen readers
- voice input
- keyboard navigation
- high contrast mode
- reduced motion

---

# Error Handling

If the AI cannot understand an action

Avoid

```
Invalid command.
```

Instead

```
Nothing in the current scene suggests how that would work.

Try asking a character or inspecting your surroundings.
```

The world should remain immersive.

---

# Design Principles

Interactions should feel

- natural
- immersive
- meaningful
- consequence-driven

The player should always feel that they are acting within the universe, not issuing commands to an AI.