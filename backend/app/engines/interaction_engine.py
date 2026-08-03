"""
Interaction Engine for Headcanon.

The controller between the user/frontend and the simulation backend.
Parses user intent, validates actions against the current scene and universe rules,
routes requests to CharacterEngine or SceneEngine, and returns structured
InteractionResult models with pending world effects.

Reference: docs/engines/03_interaction_engine.md
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.engines.character_engine import CharacterEngine
from app.engines.scene_engine import SceneEngine
from app.world.scene import Scene
from app.world.universe import Universe
from app.world.world_state import WorldState

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "interaction"


class ParsedAction(BaseModel, frozen=True):
    """Parsed representation of a user action."""

    action: str  # e.g. "talk", "observe", "inspect", "travel", "use", "give", "wait"
    target: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    raw_input: str = ""


class InteractionResult(BaseModel, frozen=True):
    """
    Structured outcome of a user interaction.

    Does NOT directly mutate the WorldState on disk. Pending changes are returned
    in pending_world_effects for the Simulation Engine.
    """

    interaction_id: str = Field(min_length=1)
    action: str = Field(min_length=1)
    target: str | None = None
    dialogue: str | None = None
    narration: str = ""
    scene: Scene | None = None
    suggested_actions: list[str] = Field(default_factory=list)
    pending_world_effects: list[dict[str, Any]] = Field(default_factory=list)
    success: bool = True
    error_message: str | None = None


class InteractionEngine:
    """
    The interaction controller for Headcanon.

    Responsibilities:
      - Accept user action string
      - Parse intent & target (via action_parser prompt or heuristic parser)
      - Validate action against current scene, reachability, and world rules
      - Route requests to downstream engines (CharacterEngine, SceneEngine)
      - Return structured InteractionResult with pending_world_effects

    Args:
        ai_client: Optional injected AI client.
        character_engine: Optional CharacterEngine instance.
        scene_engine: Optional SceneEngine instance.
        prompt_dir: Path to interaction prompt directory.
    """

    def __init__(
        self,
        ai_client: Any = None,
        character_engine: CharacterEngine | None = None,
        scene_engine: SceneEngine | None = None,
        prompt_dir: Path = _PROMPT_DIR,
    ) -> None:
        self.ai_client = ai_client
        self.character_engine = character_engine
        self.scene_engine = scene_engine or SceneEngine(ai_client)
        self.prompt_dir = prompt_dir
        self._prompts: dict[str, str] = {}
        self._load_prompts()

        # Action Handler Registry (Extensible Strategy Pattern)
        self._action_handlers: dict[
            str,
            Callable[[ParsedAction, Scene, WorldState, Universe], InteractionResult],
        ] = {
            "talk": self._handle_talk,
            "observe": self._handle_observe,
            "inspect": self._handle_inspect,
            "travel": self._handle_travel,
            "use": self._handle_use,
            "give": self._handle_give,
            "wait": self._handle_wait,
        }

    def _load_prompts(self) -> None:
        """Pre-load interaction prompt templates."""
        if self.prompt_dir.exists():
            for file in self.prompt_dir.glob("*.txt"):
                self._prompts[file.name] = file.read_text(encoding="utf-8")

    def register_action_handler(
        self,
        action_name: str,
        handler: Callable[[ParsedAction, Scene, WorldState, Universe], InteractionResult],
    ) -> None:
        """Register a new action handler strategy dynamically."""
        self._action_handlers[action_name.lower()] = handler

    def parse_action(self, user_input: str, scene: Scene | None = None) -> ParsedAction:
        """
        Parse raw user input into an intent, target, and parameters.

        Uses LLM action_parser.txt if ai_client is available, or fallback regex parser.
        """
        inp = user_input.strip()
        if not inp:
            return ParsedAction(action="observe", raw_input=inp)

        # 1. Try LLM action parser if available
        if self.ai_client is not None and "action_parser.txt" in self._prompts:
            template = self._prompts["action_parser.txt"]
            scene_ctx = scene.location.name if scene else "Unknown Scene"
            prompt = template.replace("{user_input}", inp).replace("{scene_context}", scene_ctx)
            try:
                raw_res = self.ai_client.generate(prompt)
                parsed_json = _parse_json(raw_res)
                act = str(parsed_json.get("action", "")).lower()
                tgt = parsed_json.get("target")
                params = parsed_json.get("parameters", {})
                if act in self._action_handlers:
                    return ParsedAction(
                        action=act,
                        target=tgt if isinstance(tgt, str) else None,
                        parameters=params if isinstance(params, dict) else {},
                        raw_input=inp,
                    )
            except Exception as exc:
                logger.warning("LLM action parsing failed: %s", exc)

        # 2. Heuristic Regex Fallback Parser
        lower = inp.lower()
        if lower.startswith(("talk to ", "speak to ", "ask ", "tell ")):
            match = re.search(r"(?:talk to|speak to|ask|tell)\s+([a-zA-Z0-9_\s]+)", inp, re.I)
            target = match.group(1).strip() if match else None
            return ParsedAction(action="talk", target=target, raw_input=inp)

        if lower.startswith(("inspect ", "examine ", "look at ", "check ")):
            match = re.search(r"(?:inspect|examine|look at|check)\s+([a-zA-Z0-9_\s]+)", inp, re.I)
            target = match.group(1).strip() if match else None
            return ParsedAction(action="inspect", target=target, raw_input=inp)

        if lower.startswith(("travel to ", "go to ", "walk to ", "move to ")):
            match = re.search(r"(?:travel to|go to|walk to|move to)\s+([a-zA-Z0-9_\s]+)", inp, re.I)
            target = match.group(1).strip() if match else None
            return ParsedAction(action="travel", target=target, raw_input=inp)

        if lower.startswith(("use ", "operate ")):
            match = re.search(r"(?:use|operate)\s+([a-zA-Z0-9_\s]+)", inp, re.I)
            target = match.group(1).strip() if match else None
            return ParsedAction(action="use", target=target, raw_input=inp)

        if lower.startswith(("give ", "hand ")):
            match = re.search(
                r"(?:give|hand)\s+([a-zA-Z0-9_\s]+)\s+to\s+([a-zA-Z0-9_\s]+)", inp, re.I
            )
            item = match.group(1).strip() if match else None
            recipient = match.group(2).strip() if match else None
            return ParsedAction(
                action="give",
                target=recipient,
                parameters={"item": item},
                raw_input=inp,
            )

        if lower in ("wait", "pass time", "do nothing"):
            return ParsedAction(action="wait", raw_input=inp)

        # Default to observe / look around
        return ParsedAction(action="observe", raw_input=inp)

    def validate_action(
        self,
        parsed_action: ParsedAction,
        scene: Scene,
        world_state: WorldState,
        universe: Universe,
    ) -> tuple[bool, str | None]:
        """
        Validate whether the action is permitted in the current scene and universe rules.

        Returns:
            Tuple of (is_valid, error_message).
        """
        act = parsed_action.action.lower()
        if act not in self._action_handlers:
            return False, f"Unsupported action '{act}'."

        tgt = parsed_action.target

        # Talk validation
        if act == "talk":
            if not tgt:
                return False, "Target character is required for talk action."
            # Check target character exists and is visible
            resolved_char = _resolve_character(tgt, scene, universe)
            if not resolved_char:
                return False, f"Character '{tgt}' is not present or visible in this scene."

        # Travel validation
        if act == "travel":
            if not tgt:
                return False, "Target destination is required for travel action."
            resolved_loc = _resolve_location(tgt, scene, universe)
            if not resolved_loc:
                return False, f"Destination '{tgt}' is not reachable from this location."

        # Inspect validation
        if act == "inspect":
            if tgt:
                # Check entity exists in scene
                is_char = _resolve_character(tgt, scene, universe) is not None
                is_obj = _resolve_object(tgt, scene, universe) is not None
                is_loc = tgt.lower() in (
                    scene.location.name.lower(),
                    scene.location.location_id.lower(),
                )
                if not (is_char or is_obj or is_loc):
                    return False, f"Target '{tgt}' to inspect was not found in this scene."

        return True, None

    def process_action(
        self,
        user_input: str,
        world_state: WorldState,
        universe: Universe,
        current_scene: Scene | None = None,
        user_character_id: str = "char_user",
    ) -> InteractionResult:
        """
        Process user input through the full interaction pipeline.

        Pipeline:
          1. Build current scene if not provided
          2. Parse user input into intent & target
          3. Validate action against scene and universe rules
          4. Route request to registered action handler strategy
          5. Return InteractionResult with pending_world_effects

        Args:
            user_input: Raw input string from player.
            world_state: Live WorldState model.
            universe: Canonical Universe model.
            current_scene: Optional active Scene.
            user_character_id: ID of player character.

        Returns:
            Structured InteractionResult model instance.
        """
        scene = current_scene or self.scene_engine.build_scene(
            universe=universe,
            world_state=world_state,
            user_character_id=user_character_id,
        )

        parsed = self.parse_action(user_input, scene)

        is_valid, error_msg = self.validate_action(parsed, scene, world_state, universe)
        if not is_valid:
            return InteractionResult(
                interaction_id=f"int_{uuid.uuid4().hex[:6]}",
                action=parsed.action,
                target=parsed.target,
                scene=scene,
                suggested_actions=scene.available_actions,
                success=False,
                error_message=error_msg or "Invalid action.",
            )

        handler = self._action_handlers[parsed.action.lower()]
        return handler(parsed, scene, world_state, universe)

    # -----------------------------------------------------------------------
    # Action Handler Strategies
    # -----------------------------------------------------------------------

    def _handle_talk(
        self,
        parsed: ParsedAction,
        scene: Scene,
        world_state: WorldState,
        universe: Universe,
    ) -> InteractionResult:
        target_char = _resolve_character(parsed.target or "", scene, universe)
        target_id = target_char.character_id if target_char else parsed.target or ""

        dialogue = "Hello."
        narration = f"You speak to {target_char.name if target_char else target_id}."
        pending_effects: list[dict[str, Any]] = []

        if self.character_engine is not None:
            try:
                char_resp = self.character_engine.generate_response(
                    character_id=target_id,
                    world_state=world_state,
                    universe=universe,
                    user_action=parsed.raw_input,
                    scene_narration=scene.narration,
                )
                dialogue = char_resp.dialogue
                narration = f"{target_char.name if target_char else target_id}: '{dialogue}'"

                # Convert response memory/relationship changes into pending effects
                if char_resp.memory_candidates:
                    pending_effects.append(
                        {"type": "suggest_memories", "candidates": char_resp.memory_candidates}
                    )
                if char_resp.relationship_changes:
                    pending_effects.append(
                        {"type": "suggest_relationships", "changes": char_resp.relationship_changes}
                    )
            except Exception as exc:
                logger.warning("CharacterEngine response failed: %s", exc)

        return InteractionResult(
            interaction_id=f"int_{uuid.uuid4().hex[:6]}",
            action="talk",
            target=target_id,
            dialogue=dialogue,
            narration=narration,
            scene=scene,
            suggested_actions=scene.available_actions,
            pending_world_effects=pending_effects,
            success=True,
        )

    def _handle_observe(
        self,
        parsed: ParsedAction,
        scene: Scene,
        world_state: WorldState,
        universe: Universe,
    ) -> InteractionResult:
        narration = self.scene_engine.generate_narration(
            location=universe.get_location(scene.location.location_id) or universe.locations[0],
            visible_characters=scene.characters,
            time_str=scene.timestamp or "",
            weather_str=scene.environment.weather or "Clear",
        )
        return InteractionResult(
            interaction_id=f"int_{uuid.uuid4().hex[:6]}",
            action="observe",
            narration=narration,
            scene=scene,
            suggested_actions=scene.available_actions,
            success=True,
        )

    def _handle_inspect(
        self,
        parsed: ParsedAction,
        scene: Scene,
        world_state: WorldState,
        universe: Universe,
    ) -> InteractionResult:
        target_name = parsed.target or "surroundings"
        char = _resolve_character(target_name, scene, universe)
        obj = _resolve_object(target_name, scene, universe)

        if char:
            narration = (
                f"You observe {char.name}. They appear {char.current_emotion or 'calm'} "
                f"and are {char.current_activity or 'present'}."
            )
        elif obj:
            narration = f"You inspect the {obj.name}. Category: {obj.category or 'Item'}."
        else:
            narration = f"You closely examine the {target_name} at {scene.location.name}."

        return InteractionResult(
            interaction_id=f"int_{uuid.uuid4().hex[:6]}",
            action="inspect",
            target=parsed.target,
            narration=narration,
            scene=scene,
            suggested_actions=scene.available_actions,
            success=True,
        )

    def _handle_travel(
        self,
        parsed: ParsedAction,
        scene: Scene,
        world_state: WorldState,
        universe: Universe,
    ) -> InteractionResult:
        dest = _resolve_location(parsed.target or "", scene, universe)
        dest_id = dest if dest else parsed.target or ""
        dest_loc = universe.get_location(dest_id)
        dest_name = dest_loc.name if dest_loc else dest_id

        narration = f"You prepare to travel to {dest_name}."
        pending_effects = [{"type": "location_update", "target_location": dest_id}]

        return InteractionResult(
            interaction_id=f"int_{uuid.uuid4().hex[:6]}",
            action="travel",
            target=dest_id,
            narration=narration,
            scene=scene,
            suggested_actions=scene.available_actions,
            pending_world_effects=pending_effects,
            success=True,
        )

    def _handle_use(
        self,
        parsed: ParsedAction,
        scene: Scene,
        world_state: WorldState,
        universe: Universe,
    ) -> InteractionResult:
        obj = _resolve_object(parsed.target or "", scene, universe)
        obj_id = obj.object_id if obj else parsed.target or ""
        narration = f"You use the {obj.name if obj else obj_id}."
        pending_effects = [{"type": "use_item", "item_id": obj_id}]

        return InteractionResult(
            interaction_id=f"int_{uuid.uuid4().hex[:6]}",
            action="use",
            target=obj_id,
            narration=narration,
            scene=scene,
            suggested_actions=scene.available_actions,
            pending_world_effects=pending_effects,
            success=True,
        )

    def _handle_give(
        self,
        parsed: ParsedAction,
        scene: Scene,
        world_state: WorldState,
        universe: Universe,
    ) -> InteractionResult:
        char = _resolve_character(parsed.target or "", scene, universe)
        char_id = char.character_id if char else parsed.target or ""
        item_id = str(parsed.parameters.get("item", "item"))

        narration = f"You offer {item_id} to {char.name if char else char_id}."
        pending_effects = [{"type": "transfer_item", "item_id": item_id, "recipient": char_id}]

        return InteractionResult(
            interaction_id=f"int_{uuid.uuid4().hex[:6]}",
            action="give",
            target=char_id,
            narration=narration,
            scene=scene,
            suggested_actions=scene.available_actions,
            pending_world_effects=pending_effects,
            success=True,
        )

    def _handle_wait(
        self,
        parsed: ParsedAction,
        scene: Scene,
        world_state: WorldState,
        universe: Universe,
    ) -> InteractionResult:
        narration = "You wait quietly as time passes."
        pending_effects = [{"type": "advance_time", "hours": 1}]

        return InteractionResult(
            interaction_id=f"int_{uuid.uuid4().hex[:6]}",
            action="wait",
            narration=narration,
            scene=scene,
            suggested_actions=scene.available_actions,
            pending_world_effects=pending_effects,
            success=True,
        )


# ---------------------------------------------------------------------------
# Helper Entity Resolution Functions
# ---------------------------------------------------------------------------


def _resolve_character(target_str: str, scene: Scene, universe: Universe) -> Any | None:
    if not target_str:
        return None
    lower_tgt = target_str.lower()
    for c in scene.characters:
        if (
            c.character_id.lower() == lower_tgt
            or c.name.lower() == lower_tgt
            or lower_tgt in c.name.lower()
        ):
            return c
    return None


def _resolve_object(target_str: str, scene: Scene, universe: Universe) -> Any | None:
    if not target_str:
        return None
    lower_tgt = target_str.lower()
    for o in scene.objects:
        if (
            o.object_id.lower() == lower_tgt
            or o.name.lower() == lower_tgt
            or lower_tgt in o.name.lower()
        ):
            return o
    return None


def _resolve_location(target_str: str, scene: Scene, universe: Universe) -> str | None:
    if not target_str:
        return None
    lower_tgt = target_str.lower()
    for conn_id in scene.location.connected_locations:
        loc = universe.get_location(conn_id)
        if conn_id.lower() == lower_tgt or (loc and loc.name.lower() == lower_tgt):
            return conn_id
    return None


def _parse_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return json.loads(text, strict=False)
