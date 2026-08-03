"""
Narration Engine for Headcanon.

Transforms Scene models and WorldState context into sensory, universe-faithful prose.
Speaks as the voice of the universe itself.

Reference: docs/engines/09_narration_engine.md
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.world.scene import Scene

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "media"


class NarrationResult(BaseModel, frozen=True):
    """
    Structured outcome of narration script generation.

    Attributes:
        scene_id: ID of the input Scene.
        narration_text: Generated narrative prose.
        sensory_details: List of sensory cues included in description.
        atmosphere: Mood / atmosphere label (e.g. "Calm", "Tense").
    """

    scene_id: str = Field(min_length=1)
    narration_text: str = Field(min_length=1)
    sensory_details: list[str] = Field(default_factory=list)
    atmosphere: str = "Calm"


class NarrationEngine:
    """
    The narrative presentation engine for Headcanon.

    Responsibilities:
      - Convert Scene objects into rich, sensory narration
      - Preserve emotional tone, pacing, and universe rules
      - Return structured NarrationResult
      - Fail gracefully without interrupting gameplay

    Args:
        ai_client: Optional injected AI client.
        prompt_dir: Path to media prompts directory.
    """

    def __init__(self, ai_client: Any = None, prompt_dir: Path = _PROMPT_DIR) -> None:
        self.ai_client = ai_client
        self.prompt_dir = prompt_dir
        self._prompts: dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Pre-load media prompts."""
        if self.prompt_dir.exists():
            for file in self.prompt_dir.glob("*.txt"):
                self._prompts[file.name] = file.read_text(encoding="utf-8")

    def generate_narration(self, scene: Scene) -> NarrationResult:
        """
        Generate narration prose and sensory details for a Scene.

        Args:
            scene: Input Scene model.

        Returns:
            Validated NarrationResult model.
        """
        # Fallback default if LLM fails or is unavailable
        fallback_text = (
            scene.narration or f"You stand at {scene.location.name}. {scene.location.description}"
        )
        fallback_res = NarrationResult(
            scene_id=scene.scene_id,
            narration_text=fallback_text,
            sensory_details=["sight"],
            atmosphere="Calm",
        )

        if self.ai_client is None or "narration.txt" not in self._prompts:
            return fallback_res

        template = self._prompts["narration.txt"]
        visible_chars = ", ".join(c.name for c in scene.characters) or "None"
        visible_objs = ", ".join(o.name for o in scene.objects) or "None"

        prompt = (
            template.replace("{location_name}", scene.location.name)
            .replace("{location_description}", scene.location.description)
            .replace("{time_of_day}", scene.environment.time_of_day or "Day")
            .replace("{weather}", scene.environment.weather or "Clear")
            .replace("{visible_characters}", visible_chars)
            .replace("{visible_objects}", visible_objs)
            .replace("{scene_narration}", scene.narration)
        )

        try:
            raw_res = self.ai_client.generate(prompt)
            data = _parse_json_or_text(raw_res)
            if isinstance(data, dict):
                text = str(data.get("narration", data.get("text", fallback_text))).strip()
                sensory = data.get("sensory_details", ["sight"])
                atmo = str(data.get("atmosphere", "Calm"))
                return NarrationResult(
                    scene_id=scene.scene_id,
                    narration_text=text or fallback_text,
                    sensory_details=sensory if isinstance(sensory, list) else ["sight"],
                    atmosphere=atmo,
                )
            elif isinstance(data, str) and data.strip():
                return NarrationResult(
                    scene_id=scene.scene_id,
                    narration_text=data.strip(),
                    sensory_details=["sight"],
                    atmosphere="Calm",
                )
        except Exception as exc:
            logger.warning("NarrationEngine LLM generation failed: %s", exc)

        return fallback_res


def _parse_json_or_text(raw: str) -> dict[str, Any] | str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    try:
        return json.loads(text, strict=False)
    except Exception:
        return text
