"""
Scene Engine for Headcanon.

Translates WorldState and Universe data into explorable, UI-ready Scene objects.

Reference: docs/engines/05_scene_engine.md, docs/universe/12_scene.md
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.world.location import Location
from app.world.scene import (
    Scene,
    SceneCharacterSummary,
    SceneEnvironment,
    SceneLocationSummary,
    SceneMediaAssets,
    SceneMetadata,
    SceneObjectSummary,
)
from app.world.universe import Universe
from app.world.world_state import WorldState

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "scene"


class SceneEngine:
    """
    The exploration and scene construction engine for Headcanon.

    Responsibilities:
      - Construct explorable Scene objects from WorldState and Universe
      - Resolve visible characters and interactive objects
      - Build available actions and exit lists for UI rendering
      - Generate dynamic ambient environmental narration
      - Return structured, UI-ready Scene objects (does NOT generate binary media)

    Args:
        ai_client: Optional injected AI client for dynamic narration generation.
        prompt_dir: Path to scene prompt directory.
    """

    def __init__(self, ai_client: Any = None, prompt_dir: Path = _PROMPT_DIR) -> None:
        self.ai_client = ai_client
        self.prompt_dir = prompt_dir
        self._prompts: dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Pre-load scene prompts if directory exists."""
        if self.prompt_dir.exists():
            for file in self.prompt_dir.glob("*.txt"):
                self._prompts[file.name] = file.read_text(encoding="utf-8")

    def build_scene(
        self,
        universe: Universe,
        world_state: WorldState,
        location_id: str | None = None,
        active_narration: str | None = None,
        user_character_id: str = "char_user",
    ) -> Scene:
        """
        Construct a complete, UI-ready Scene model for the current location.

        Args:
            universe: Canonical Universe model.
            world_state: Live WorldState model.
            location_id: Optional location ID. Defaults to character's location
                         or universe default.
            active_narration: Optional custom narration string.
            user_character_id: ID of player character.

        Returns:
            Validated Scene model instance.

        Raises:
            ValueError: If location cannot be found in Universe.
        """
        # Resolve target location ID
        target_loc_id = location_id
        if not target_loc_id:
            if user_character_id in world_state.characters:
                target_loc_id = world_state.characters[user_character_id].location
            elif world_state.locations:
                target_loc_id = next(iter(world_state.locations.keys()))
            elif universe.locations:
                target_loc_id = universe.locations[0].id

        if not target_loc_id:
            raise ValueError("Cannot determine current location for scene construction.")

        location_model = universe.get_location(target_loc_id)
        if not location_model:
            raise ValueError(f"Location '{target_loc_id}' not found in Universe.")

        # 1. Resolve Location Summary
        connected_ids = [c for c in location_model.connections if c != target_loc_id]
        loc_summary = SceneLocationSummary(
            location_id=location_model.id,
            name=location_model.name,
            description=location_model.description,
            parent_location=location_model.parent_location,
            connected_locations=connected_ids,
        )

        # 2. Resolve Visible Characters
        visible_characters = self.determine_visible_characters(
            universe=universe,
            world_state=world_state,
            location_id=target_loc_id,
            user_character_id=user_character_id,
        )

        # 3. Resolve Visible Objects
        visible_objects = self.determine_visible_objects(
            universe=universe,
            world_state=world_state,
            location_id=target_loc_id,
        )

        # 4. Resolve Available Actions
        available_actions = self.determine_available_actions(
            location=location_model,
            visible_characters=visible_characters,
            visible_objects=visible_objects,
            connected_locations=connected_ids,
            universe=universe,
        )

        # 5. Build Environment Context
        time_str = f"Day {world_state.time.day}, Hour {world_state.time.hour:02d}:00"
        weather_str = world_state.environment.weather or "Clear"
        environment = SceneEnvironment(
            time_of_day="Morning" if world_state.time.hour < 12 else "Afternoon",
            weather=weather_str,
            lighting="Bright" if 6 <= world_state.time.hour <= 18 else "Dim",
            ambient_description=f"{location_model.name} under {weather_str.lower()} skies.",
        )

        # 6. Generate Narration
        narration = active_narration or self.generate_narration(
            location=location_model,
            visible_characters=visible_characters,
            time_str=time_str,
            weather_str=weather_str,
        )

        # 7. Metadata
        now = datetime.now(tz=UTC)
        metadata = SceneMetadata(
            scene_version=1,
            world_state_version=str(world_state.time.day),
            generation_timestamp=now,
        )

        scene_id = f"scene_{location_model.id}"

        return Scene(
            scene_id=scene_id,
            universe_id=universe.metadata.id,
            timestamp=time_str,
            location=loc_summary,
            narration=narration,
            characters=visible_characters,
            objects=visible_objects,
            available_actions=available_actions,
            environment=environment,
            media=SceneMediaAssets(),
            metadata=metadata,
        )

    def determine_visible_characters(
        self,
        universe: Universe,
        world_state: WorldState,
        location_id: str,
        user_character_id: str = "char_user",
    ) -> list[SceneCharacterSummary]:
        """Resolve visible characters in the location."""
        occupants: list[str] = []
        if location_id in world_state.locations:
            occupants = world_state.locations[location_id].occupants

        visible: list[SceneCharacterSummary] = []
        for cid in occupants:
            if cid == user_character_id:
                continue
            char = universe.get_character(cid)
            char_state = world_state.characters.get(cid)
            emotion = char_state.emotion.value if char_state and char_state.emotion else "Calm"
            activity = char_state.current_action if char_state else "Present"

            name = char.name if char else cid
            visible.append(
                SceneCharacterSummary(
                    character_id=cid,
                    name=name,
                    current_emotion=emotion,
                    current_activity=activity or "Standing nearby",
                    interaction_available=True,
                )
            )
        return visible

    def determine_visible_objects(
        self,
        universe: Universe,
        world_state: WorldState,
        location_id: str,
    ) -> list[SceneObjectSummary]:
        """Resolve visible interactive objects in the location."""
        obj_ids: list[str] = []
        if location_id in world_state.locations:
            obj_ids = list(world_state.locations[location_id].objects)

        visible: list[SceneObjectSummary] = []
        for oid in obj_ids:
            obj_model = universe.get_object(oid)
            name = obj_model.name if obj_model else oid
            category = obj_model.category.value if obj_model and obj_model.category else "Object"
            visible.append(
                SceneObjectSummary(
                    object_id=oid,
                    name=name,
                    category=category,
                    current_state={"visible": True},
                    interaction_options=["Inspect", "Use", "Take"],
                )
            )
        return visible

    def determine_available_actions(
        self,
        location: Location,
        visible_characters: list[SceneCharacterSummary],
        visible_objects: list[SceneObjectSummary],
        connected_locations: list[str],
        universe: Universe,
    ) -> list[str]:
        """Build structured list of available UI interaction prompts."""
        actions: list[str] = ["Observe surroundings", "Wait"]

        for char in visible_characters:
            actions.append(f"Talk to {char.name}")

        for obj in visible_objects:
            actions.append(f"Inspect {obj.name}")

        for conn_id in connected_locations:
            conn_loc = universe.get_location(conn_id)
            dest_name = conn_loc.name if conn_loc else conn_id
            actions.append(f"Travel to {dest_name}")

        return actions

    def generate_narration(
        self,
        location: Location,
        visible_characters: list[SceneCharacterSummary],
        time_str: str,
        weather_str: str,
    ) -> str:
        """Generate environmental narration using scene prompts or fallback."""
        if self.ai_client is not None and "scene_description.txt" in self._prompts:
            template = self._prompts["scene_description.txt"]
            char_names = ", ".join(c.name for c in visible_characters) or "None"
            prompt = (
                template.replace("{location_name}", location.name)
                .replace("{location_description}", location.description)
                .replace("{time_of_day}", time_str)
                .replace("{weather}", weather_str)
                .replace("{visible_characters}", char_names)
            )
            try:
                res = self.ai_client.generate(prompt).strip()
                if res:
                    return res
            except Exception as exc:
                logger.warning("Failed to generate scene narration via LLM: %s", exc)

        # Ambient narration fallback
        char_desc = (
            f" {', '.join(c.name for c in visible_characters)} can be seen nearby."
            if visible_characters
            else " The area is quiet."
        )
        return f"You are at {location.name}. {location.description}{char_desc}"
