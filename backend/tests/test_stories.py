from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_story_returns_501() -> None:
    response = client.post(
        "/api/stories",
        json={
            "universe": "Harry Potter",
            "character_name": "Elias",
            "role": "Student",
            "mood": "Dark",
            "prompt": "The castle hides an ancient secret.",
        },
    )
    assert response.status_code == 501


def test_list_stories_returns_501() -> None:
    response = client.get("/api/stories")
    assert response.status_code == 501


def test_get_story_returns_501() -> None:
    response = client.get("/api/stories/some-uuid")
    assert response.status_code == 501


def test_continue_story_returns_501() -> None:
    response = client.post(
        "/api/stories/some-uuid/continue",
        json={"prompt": "Continue from the dragon fight."},
    )
    assert response.status_code == 501


def test_regenerate_scene_returns_501() -> None:
    response = client.post(
        "/api/stories/some-uuid/regenerate-scene",
        json={"scene_number": 2},
    )
    assert response.status_code == 501


def test_delete_story_returns_501() -> None:
    response = client.delete("/api/stories/some-uuid")
    assert response.status_code == 501
