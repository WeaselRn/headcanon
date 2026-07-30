"""Unit tests for StoryService.generate() with a mocked GeminiClient."""

import json
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.schemas.generation import GenerationRequest
from app.services.story_service import StoryService, _parse_json

# ---------------------------------------------------------------------------
# _parse_json helper
# ---------------------------------------------------------------------------


def test_parse_json_plain() -> None:
    data = {"title": "Test", "story": "...", "scenes": []}
    assert _parse_json(json.dumps(data)) == data


def test_parse_json_strips_markdown_fence() -> None:
    raw = '```json\n{"title": "T"}\n```'
    assert _parse_json(raw) == {"title": "T"}


def test_parse_json_strips_plain_fence() -> None:
    raw = '```\n{"title": "T"}\n```'
    assert _parse_json(raw) == {"title": "T"}


def test_parse_json_invalid_raises_value_error() -> None:
    with pytest.raises(ValueError, match="invalid JSON"):
        _parse_json("not json at all")


# ---------------------------------------------------------------------------
# StoryService.generate
# ---------------------------------------------------------------------------

_GEMINI_RESPONSE = {
    "title": "The Hidden Chamber",
    "story": "A long immersive story about Elias discovering ancient secrets.",
    "scenes": [
        {
            "scene_number": 1,
            "title": "The Dark Corridor",
            "description": "Elias walks through a torchlit hallway.",
            "image_prompt": "Dark stone corridor with flickering torches.",
            "image_url": "",
        },
        {
            "scene_number": 2,
            "title": "The Hidden Door",
            "description": "A door appears behind a tapestry.",
            "image_prompt": "Ancient wooden door behind a tattered tapestry.",
            "image_url": "",
        },
    ],
}

_REQUEST = GenerationRequest(
    universe="Harry Potter",
    character_name="Elias",
    role="Student",
    mood="Dark",
    prompt="The castle hides an ancient secret.",
)


def _make_service(gemini_text: str) -> StoryService:
    mock_gemini = MagicMock()
    mock_gemini.load_prompt.return_value = (
        "Universe: {universe}\nCharacter: {character_name}\n"
        "Role: {role}\nMood: {mood}\nPrompt: {prompt}"
    )
    mock_gemini.generate_text.return_value = gemini_text
    return StoryService(gemini=mock_gemini)


def test_generate_returns_story() -> None:
    service = _make_service(json.dumps(_GEMINI_RESPONSE))
    story = service.generate(_REQUEST)

    assert story.title == "The Hidden Chamber"
    assert story.universe == "Harry Potter"
    assert story.character_name == "Elias"
    assert story.role == "Student"
    assert story.mood == "Dark"
    assert len(story.scenes) == 2
    assert story.scenes[0].scene_number == 1
    assert story.scenes[1].title == "The Hidden Door"
    assert story.story_id  # non-empty UUID
    assert story.metadata.pipeline_version == "v1"
    assert "gemini-2.0-flash" in story.metadata.models


def test_generate_scene_image_url_is_empty() -> None:
    service = _make_service(json.dumps(_GEMINI_RESPONSE))
    story = service.generate(_REQUEST)
    for scene in story.scenes:
        assert scene.image_url == ""


def test_generate_metadata_timestamps_are_recent() -> None:
    service = _make_service(json.dumps(_GEMINI_RESPONSE))
    story = service.generate(_REQUEST)
    now = datetime.now(tz=UTC)
    delta = (now - story.metadata.created_at).total_seconds()
    assert delta < 5


def test_generate_raises_value_error_on_bad_json() -> None:
    service = _make_service("this is not json")
    with pytest.raises(ValueError):
        service.generate(_REQUEST)


def test_generate_parses_markdown_wrapped_json() -> None:
    wrapped = f"```json\n{json.dumps(_GEMINI_RESPONSE)}\n```"
    service = _make_service(wrapped)
    story = service.generate(_REQUEST)
    assert story.title == "The Hidden Chamber"
