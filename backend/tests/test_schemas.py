import pytest
from pydantic import ValidationError

from app.schemas.generation import (
    ContinueStoryRequest,
    GenerationRequest,
    RegenerateSceneRequest,
)


def test_generation_request_valid() -> None:
    req = GenerationRequest(
        universe="Harry Potter",
        character_name="Elias",
        role="Student",
        mood="Dark",
        prompt="The castle hides an ancient secret.",
    )
    assert req.universe == "Harry Potter"
    assert req.character_name == "Elias"


def test_generation_request_missing_field() -> None:
    with pytest.raises(ValidationError):
        GenerationRequest(universe="Harry Potter")  # type: ignore[call-arg]


def test_continue_story_request_valid() -> None:
    req = ContinueStoryRequest(prompt="Continue from the dragon fight.")
    assert req.prompt == "Continue from the dragon fight."


def test_regenerate_scene_request_valid() -> None:
    req = RegenerateSceneRequest(scene_number=2)
    assert req.scene_number == 2
