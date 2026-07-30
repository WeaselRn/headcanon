"""Unit tests for StoryService with a mocked GeminiClient."""

import json
from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.models.metadata import StoryMetadata
from app.models.scene import Scene
from app.models.story import Story
from app.schemas.generation import ContinueStoryRequest, GenerationRequest
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

_CONTINUE_RESPONSE = {
    "continuation_text": "Elias stepped through the hidden door into the darkness beyond.",
    "scenes": [
        {
            "scene_number": 3,
            "title": "Into the Dark",
            "description": "Elias explores the inner chamber.",
            "image_prompt": "A hidden chamber filled with glowing runes.",
            "image_url": "",
        }
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

    def _load_prompt(filename: str) -> str:
        if filename == "continue_story.txt":
            return (
                "Universe: {universe}\nCharacter: {character_name}\n"
                "Role: {role}\nMood: {mood}\nPrompt: {prompt}\n"
                "Current Story: {current_story}\nNext Scene Number: {next_scene_number}"
            )
        return (
            "Universe: {universe}\nCharacter: {character_name}\n"
            "Role: {role}\nMood: {mood}\nPrompt: {prompt}"
        )

    mock_gemini.load_prompt.side_effect = _load_prompt
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


def test_generate_continuation_raw() -> None:
    service = _make_service(json.dumps(_CONTINUE_RESPONSE))
    now = datetime.now(tz=UTC)
    existing_story = Story(
        story_id="cont-uuid-1",
        title="Title",
        universe="HP",
        character_name="Elias",
        role="Student",
        mood="Dark",
        story="Chapter 1 content.",
        scenes=[
            Scene(
                scene_number=1,
                title="S1",
                description="D1",
                image_prompt="P1",
                image_url="",
            ),
            Scene(
                scene_number=2,
                title="S2",
                description="D2",
                image_prompt="P2",
                image_url="",
            ),
        ],
        metadata=StoryMetadata(created_at=now, updated_at=now, models=[], pipeline_version="v1"),
    )

    req = ContinueStoryRequest(prompt="Explore the chamber.")
    text, scenes = service.generate_continuation_raw(existing_story, req)

    assert "Elias stepped through the hidden door" in text
    assert len(scenes) == 1
    assert scenes[0].scene_number == 3
    assert scenes[0].title == "Into the Dark"


def test_continue_story_with_storage() -> None:
    mock_gemini = MagicMock()

    def _load_prompt(filename: str) -> str:
        if filename == "continue_story.txt":
            return (
                "Universe: {universe}\nCharacter: {character_name}\n"
                "Role: {role}\nMood: {mood}\nPrompt: {prompt}\n"
                "Current Story: {current_story}\nNext Scene Number: {next_scene_number}"
            )
        return (
            "Universe: {universe}\nCharacter: {character_name}\n"
            "Role: {role}\nMood: {mood}\nPrompt: {prompt}"
        )

    mock_gemini.load_prompt.side_effect = _load_prompt
    mock_gemini.generate_text.return_value = json.dumps(_CONTINUE_RESPONSE)

    now = datetime.now(tz=UTC)
    existing_story = Story(
        story_id="cont-uuid-1",
        title="Title",
        universe="HP",
        character_name="Elias",
        role="Student",
        mood="Dark",
        story="Chapter 1 content.",
        scenes=[
            Scene(
                scene_number=1,
                title="S1",
                description="D1",
                image_prompt="P1",
                image_url="",
            ),
            Scene(
                scene_number=2,
                title="S2",
                description="D2",
                image_prompt="P2",
                image_url="",
            ),
        ],
        metadata=StoryMetadata(created_at=now, updated_at=now, models=[], pipeline_version="v1"),
    )

    mock_storage = MagicMock()
    mock_storage.get_story.return_value = existing_story

    service = StoryService(gemini=mock_gemini, storage=mock_storage)
    req = ContinueStoryRequest(prompt="Explore the chamber.")

    updated_story = service.continue_story("cont-uuid-1", req)

    mock_storage.get_story.assert_called_once_with("cont-uuid-1")
    assert "Chapter 1 content." in updated_story.story
    assert "Elias stepped through the hidden door" in updated_story.story
    assert len(updated_story.scenes) == 3
    assert updated_story.scenes[2].scene_number == 3
    mock_storage.save_story.assert_called_once()
