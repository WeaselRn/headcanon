import json
import logging
from datetime import UTC, datetime
from typing import Any

from app.models.metadata import StoryMetadata
from app.models.scene import Scene
from app.models.story import Story, StoryCard
from app.schemas.generation import ContinueStoryRequest, GenerationRequest
from app.services.gemini_client import GeminiClient
from app.services.storage_service import StorageService
from app.utils.helpers import generate_id

logger = logging.getLogger(__name__)

_PIPELINE_VERSION = "v1"
_GEMINI_MODEL = "gemini-2.0-flash"


class StoryService:
    def __init__(self, gemini: GeminiClient, storage: StorageService | None = None) -> None:
        self._gemini = gemini
        self._storage = storage

    def generate_raw(self, request: GenerationRequest) -> Story:
        logger.info(
            "Generating raw story text: universe=%s character=%s",
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
        return story

    def generate_continuation_raw(
        self, existing_story: Story, request: ContinueStoryRequest
    ) -> tuple[str, list[Scene]]:
        logger.info("Generating story continuation for id=%s", existing_story.story_id)

        next_scene_number = max([s.scene_number for s in existing_story.scenes], default=0) + 1

        template = self._gemini.load_prompt("continue_story.txt")
        prompt = template.format(
            universe=existing_story.universe,
            character_name=existing_story.character_name,
            role=existing_story.role,
            mood=existing_story.mood,
            current_story=existing_story.story,
            prompt=request.prompt,
            next_scene_number=next_scene_number,
        )

        raw = self._gemini.generate_text(prompt)
        data: dict[str, Any] = _parse_json(raw)

        continuation_text = str(data["continuation_text"])
        new_scenes = [
            Scene(
                scene_number=s["scene_number"],
                title=s["title"],
                description=s["description"],
                image_prompt=s["image_prompt"],
                image_url=s.get("image_url", ""),
            )
            for s in data["scenes"]
        ]

        return continuation_text, new_scenes

    # ------------------------------------------------------------------
    # POST /stories
    # ------------------------------------------------------------------
    def generate(self, request: GenerationRequest) -> Story:
        story = self.generate_raw(request)

        if self._storage is not None:
            self._storage.save_story(story)

        logger.info("Story generated: id=%s title=%r", story.story_id, story.title)
        return story

    # ------------------------------------------------------------------
    # GET /stories
    # ------------------------------------------------------------------
    def list_stories(self) -> list[StoryCard]:
        if self._storage is not None:
            return self._storage.list_stories()
        raise NotImplementedError

    # ------------------------------------------------------------------
    # GET /stories/{story_id}
    # ------------------------------------------------------------------
    def get_story(self, story_id: str) -> Story:
        if self._storage is not None:
            return self._storage.get_story(story_id)
        raise NotImplementedError

    # ------------------------------------------------------------------
    # POST /stories/{story_id}/continue
    # ------------------------------------------------------------------
    def continue_story(self, story_id: str, request: ContinueStoryRequest) -> Story:
        if self._storage is None:
            raise NotImplementedError
        story = self._storage.get_story(story_id)
        continuation_text, new_scenes = self.generate_continuation_raw(story, request)

        story.story = f"{story.story}\n\n{continuation_text}"
        story.scenes.extend(new_scenes)
        story.metadata.updated_at = datetime.now(tz=UTC)

        self._storage.save_story(story)
        logger.info("Story continued for id=%s", story_id)
        return story

    # ------------------------------------------------------------------
    # DELETE /stories/{story_id}
    # ------------------------------------------------------------------
    def delete_story(self, story_id: str) -> None:
        if self._storage is not None:
            self._storage.delete_story(story_id)
            return
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
