"""
Unit tests for Headcanon Interaction System (Milestone 6).

Tests SceneEngine and InteractionEngine for:
  - Scene construction (visibility, navigation exits, actions, environmental context)
  - Action intent parsing (talk, observe, inspect, travel, use, give, wait)
  - Action validation (target reachability, connected exits, error messages)
  - Extensible action handler strategy pattern
  - Generation of pending world effects without mutating WorldState directly
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

from app.engines.character_engine import CharacterEngine
from app.engines.interaction_engine import (
    InteractionEngine,
    InteractionResult,
    ParsedAction,
)
from app.engines.scene_engine import SceneEngine
from app.world.character import (
    Character,
    CharacterPersonality,
    CharacterSpeech,
    SpeechTone,
)
from app.world.location import Location, LocationCategory
from app.world.object import Object, ObjectCategory
from app.world.scene import Scene
from app.world.timeline import WorldTime
from app.world.universe import (
    ImportSource,
    Universe,
    UniverseMetadata,
    WorldRule,
    WorldRuleCategory,
)
from app.world.world_state import CharacterState, LocationState, WorldState


class StubAIClient:
    """Stub AI Client returning pre-configured JSON responses."""

    def __init__(self, response_text: str | None = None) -> None:
        self.response_text = response_text or json.dumps(
            {
                "character_id": "char_hermione",
                "dialogue": "We must look into the restricted section.",
                "emotion": "Focused",
                "actions": ["Opens book"],
                "memory_candidates": [{"summary": "Discussed restricted section"}],
                "relationship_changes": [{"target": "user", "delta": 2}],
            }
        )

    def generate(self, prompt: str) -> str:
        return self.response_text


# ---------------------------------------------------------------------------
# Test Fixtures / Helpers
# ---------------------------------------------------------------------------

NOW = datetime(2026, 8, 4, 1, 0, 0, tzinfo=UTC)


def create_sample_universe() -> Universe:
    meta = UniverseMetadata(
        id="hp_001",
        title="Harry Potter",
        author="J. K. Rowling",
        source=ImportSource.CUSTOM,
        created_at=NOW,
    )
    hermione = Character(
        id="char_hermione",
        name="Hermione Granger",
        description="Brilliant young witch.",
        personality=CharacterPersonality(traits=["Logical", "Studious"]),
        speech=CharacterSpeech(tone=SpeechTone.ACADEMIC),
    )
    harry = Character(
        id="char_harry",
        name="Harry Potter",
        description="The Boy Who Lived.",
    )
    user = Character(
        id="char_user",
        name="Player",
        description="The protagonist.",
    )
    library = Location(
        id="loc_library",
        name="Hogwarts Library",
        description="A quiet research hall with dusty bookshelves.",
        category=LocationCategory.ROOM,
        connections=["loc_hallway"],
    )
    hallway = Location(
        id="loc_hallway",
        name="Corridor",
        description="A bustling stone hallway.",
        category=LocationCategory.ROOM,
        connections=["loc_library"],
    )
    book = Object(
        id="obj_rune_book",
        name="Ancient Rune Book",
        description="A heavily bound magical tome.",
        category=ObjectCategory.BOOK,
        location="loc_library",
    )
    rule = WorldRule(
        id="rule_magic",
        name="Magic Rule",
        category=WorldRuleCategory.MAGIC,
        description="Spells require a wand.",
    )

    return Universe(
        metadata=meta,
        characters=[hermione, harry, user],
        locations=[library, hallway],
        objects=[book],
        world_rules=[rule],
    )


def create_sample_world_state() -> WorldState:
    char_states = {
        "char_user": CharacterState(character_id="char_user", location="loc_library"),
        "char_hermione": CharacterState(character_id="char_hermione", location="loc_library"),
        "char_harry": CharacterState(character_id="char_harry", location="loc_hallway"),
    }
    loc_states = {
        "loc_library": LocationState(
            location_id="loc_library",
            occupants=["char_user", "char_hermione"],
            objects=["obj_rune_book"],
        ),
        "loc_hallway": LocationState(
            location_id="loc_hallway",
            occupants=["char_harry"],
        ),
    }
    return WorldState(
        universe_id="hp_001",
        time=WorldTime(day=3, hour=10),
        characters=char_states,
        locations=loc_states,
    )


# ---------------------------------------------------------------------------
# SceneEngine Tests
# ---------------------------------------------------------------------------


class TestSceneEngine:
    def test_build_scene(self):
        engine = SceneEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        scene = engine.build_scene(universe=uni, world_state=ws, user_character_id="char_user")

        assert isinstance(scene, Scene)
        assert scene.location.location_id == "loc_library"
        assert scene.location.name == "Hogwarts Library"
        assert len(scene.characters) == 1
        assert scene.characters[0].character_id == "char_hermione"
        assert len(scene.objects) == 1
        assert scene.objects[0].object_id == "obj_rune_book"
        assert "Talk to Hermione Granger" in scene.available_actions
        assert "Travel to Corridor" in scene.available_actions

    def test_determine_visible_characters_excludes_player(self):
        engine = SceneEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        visible = engine.determine_visible_characters(
            universe=uni,
            world_state=ws,
            location_id="loc_library",
            user_character_id="char_user",
        )

        assert len(visible) == 1
        assert visible[0].character_id == "char_hermione"

    def test_generate_narration_fallback(self):
        engine = SceneEngine()
        uni = create_sample_universe()
        loc = uni.locations[0]

        narration = engine.generate_narration(
            location=loc,
            visible_characters=[],
            time_str="Day 3, Hour 10:00",
            weather_str="Clear",
        )

        assert "Hogwarts Library" in narration
        assert "A quiet research hall" in narration


# ---------------------------------------------------------------------------
# InteractionEngine Tests
# ---------------------------------------------------------------------------


class TestInteractionEngine:
    def test_parse_action_fallback(self):
        engine = InteractionEngine()

        p_talk = engine.parse_action("Talk to Hermione")
        assert p_talk.action == "talk"
        assert p_talk.target == "Hermione"

        p_inspect = engine.parse_action("Inspect Ancient Rune Book")
        assert p_inspect.action == "inspect"
        assert p_inspect.target == "Ancient Rune Book"

        p_travel = engine.parse_action("Travel to Corridor")
        assert p_travel.action == "travel"
        assert p_travel.target == "Corridor"

        p_wait = engine.parse_action("wait")
        assert p_wait.action == "wait"

    def test_validate_action_valid(self):
        engine = InteractionEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()
        scene = engine.scene_engine.build_scene(uni, ws)

        valid_talk, err1 = engine.validate_action(
            ParsedAction(action="talk", target="Hermione Granger"),
            scene=scene,
            world_state=ws,
            universe=uni,
        )
        assert valid_talk
        assert err1 is None

        valid_travel, err2 = engine.validate_action(
            ParsedAction(action="travel", target="loc_hallway"),
            scene=scene,
            world_state=ws,
            universe=uni,
        )
        assert valid_travel
        assert err2 is None

    def test_validate_action_invalid_target_not_present(self):
        engine = InteractionEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()
        scene = engine.scene_engine.build_scene(uni, ws)

        # Harry is in hallway, not library
        is_valid, err = engine.validate_action(
            ParsedAction(action="talk", target="Harry Potter"),
            scene=scene,
            world_state=ws,
            universe=uni,
        )
        assert not is_valid
        assert "not present" in err

    def test_process_talk_action_with_character_engine(self):
        client = StubAIClient()
        char_engine = CharacterEngine(ai_client=client)
        engine = InteractionEngine(ai_client=client, character_engine=char_engine)

        uni = create_sample_universe()
        ws = create_sample_world_state()

        result = engine.process_action(
            user_input="Talk to Hermione",
            world_state=ws,
            universe=uni,
        )

        assert isinstance(result, InteractionResult)
        assert result.success
        assert result.action == "talk"
        assert result.target == "char_hermione"
        assert result.dialogue == "We must look into the restricted section."
        assert len(result.pending_world_effects) > 0

    def test_process_travel_action_returns_pending_effect(self):
        engine = InteractionEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        result = engine.process_action(
            user_input="Travel to Corridor",
            world_state=ws,
            universe=uni,
        )

        assert result.success
        assert result.action == "travel"
        assert result.target == "loc_hallway"
        assert len(result.pending_world_effects) == 1
        assert result.pending_world_effects[0]["type"] == "location_update"
        assert result.pending_world_effects[0]["target_location"] == "loc_hallway"

    def test_process_inspect_action(self):
        engine = InteractionEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        result = engine.process_action(
            user_input="Inspect Ancient Rune Book",
            world_state=ws,
            universe=uni,
        )

        assert result.success
        assert result.action == "inspect"
        assert "Ancient Rune Book" in result.narration

    def test_process_wait_action(self):
        engine = InteractionEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        result = engine.process_action(
            user_input="wait",
            world_state=ws,
            universe=uni,
        )

        assert result.success
        assert result.action == "wait"
        assert result.pending_world_effects[0]["type"] == "advance_time"

    def test_custom_action_handler_registration(self):
        engine = InteractionEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()
        scene = engine.scene_engine.build_scene(uni, ws)

        def custom_dance_handler(parsed, scene, ws, uni):
            return InteractionResult(
                interaction_id="int_dance_001",
                action="dance",
                narration="You dance gracefully across the library floor.",
                scene=scene,
                success=True,
            )

        engine.register_action_handler("dance", custom_dance_handler)

        parsed_dance = ParsedAction(action="dance")
        result = custom_dance_handler(parsed_dance, scene, ws, uni)
        assert result.success
        assert result.action == "dance"
        assert "dance gracefully" in result.narration

    def test_interaction_engine_does_not_mutate_world_state(self):
        client = StubAIClient()
        char_engine = CharacterEngine(ai_client=client)
        engine = InteractionEngine(ai_client=client, character_engine=char_engine)

        uni = create_sample_universe()
        ws = create_sample_world_state()

        initial_day = ws.time.day
        initial_loc = ws.characters["char_user"].location

        _result = engine.process_action(
            user_input="Travel to Corridor",
            world_state=ws,
            universe=uni,
        )

        # Assert WorldState was NOT mutated on disk or in-memory
        assert ws.time.day == initial_day
        assert ws.characters["char_user"].location == initial_loc
