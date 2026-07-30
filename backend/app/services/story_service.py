import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.models.metadata import StoryMetadata
from app.models.scene import Scene
from app.models.story import Story, StoryCard
from app.schemas.generation import ContinueStoryRequest, GenerationRequest
from app.services.gemini_client import GeminiClient
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

_PIPELINE_VERSION = "v1"
_GEMINI_MODEL = "gemini-2.0-flash"


class StoryService:
    def __init__(self, gemini: GeminiClient) -> None:
        self._gemini = gemini

    # ------------------------------------------------------------------
    # POST /stories
    # ------------------------------------------------------------------
    def generate(self, request: GenerationRequest) -> Story:
        logger.info(
            "Generating story: universe=%s character=%s",
            request.universe,
            request.character_name,
        )

        template = self._gemini.load_prompt("story.txt")
        prompt = template.format(
            universe=request.universe,
            character_name=request.character_name,
            role=request.role,
            mood=request.mood,
            prompt=request.prompt,
        )

        raw = self._gemini.generate_text(prompt)
        data: dict[str, Any] = _parse_json(raw)

        now = datetime.now(tz=UTC)
        scenes = [
            Scene(
                scene_number=s["scene_number"],
                title=s["title"],
                description=s["description"],
                image_prompt=s["image_prompt"],
                image_url=s.get("image_url", ""),
            )
            for s in data["scenes"]
        ]

        story = Story(
            story_id=generate_id(),
            title=data["title"],
            universe=request.universe,
            character_name=request.character_name,
            role=request.role,
            mood=request.mood,
            story=data["story"],
            scenes=scenes,
            metadata=StoryMetadata(
                created_at=now,
                updated_at=now,
                models=[_GEMINI_MODEL],
                pipeline_version=_PIPELINE_VERSION,
            ),
        )

        logger.info("Story generated: id=%s title=%r", story.story_id, story.title)
        return story

    # ------------------------------------------------------------------
    # Remaining methods — not implemented in this milestone
    # ------------------------------------------------------------------
    def list_stories(self) -> list[StoryCard]:
        raise NotImplementedError

    def get_story(self, story_id: str) -> Story:
        raise NotImplementedError

    def continue_story(self, story_id: str, request: ContinueStoryRequest) -> Story:
        raise NotImplementedError

    def delete_story(self, story_id: str) -> None:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_json(raw: str) -> dict[str, Any]:
    """
    Strip any accidental markdown fences and parse JSON.
    Gemini occasionally wraps the JSON in ```json ... ``` despite instructions.
    """
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # drop first (```json or ```) and last (```) lines
        text = "\n".join(lines[1:-1]).strip()
    try:
        result: dict[str, Any] = json.loads(text)
        return result
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse Gemini JSON response: %s\nRaw:\n%s", exc, raw[:500])
        raise ValueError(f"Gemini returned invalid JSON: {exc}") from exc
