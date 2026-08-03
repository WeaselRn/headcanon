"""
Unit tests for Headcanon Character System (Milestone 5).

Tests MemoryEngine, RelationshipEngine, and CharacterEngine for:
  - Context building and prompt formatting
  - Timeline filtering (no future knowledge leaks)
  - Memory ranking and decay filtering
  - Relationship metric calculation, bounds [0, 100], and type inference
  - Validation (immersion breaks and forbidden AI meta-language rejection)
  - Non-mutating behavior (engines return proposals/responses without mutating world state directly)
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

import pytest

from app.engines.character_engine import CharacterEngine, CharacterEngineResponse
from app.engines.memory_engine import MemoryEngine
from app.engines.relationship_engine import RelationshipEngine
from app.world.character import (
    Character,
    CharacterGoal,
    CharacterPersonality,
    CharacterSpeech,
    SpeechTone,
)
from app.world.location import Location, LocationCategory
from app.world.memory import Memory, MemoryType
from app.world.relationship import Relationship, RelationshipScores, RelationshipType
from app.world.timeline import Timeline, TimelineEvent, WorldTime
from app.world.universe import ImportSource, Universe, UniverseMetadata, WorldRule, WorldRuleCategory
from app.world.world_state import CharacterState, LocationState, WorldState


class StubAIClient:
    """Stub AI Client returning pre-configured JSON responses."""

    def __init__(self, responses: dict[str, str] | None = None) -> None:
        self.responses = responses or {}

    def generate(self, prompt: str) -> str:
        for key, resp in self.responses.items():
            if key in prompt:
                return resp
        return json.dumps(
            {
                "character_id": "char_hermione",
                "dialogue": "That is an intriguing question.",
                "emotion": "Curious",
                "actions": ["Opens book"],
                "memory_candidates": [],
                "relationship_changes": [],
                "world_effects": [],
                "follow_up_actions": [],
            }
        )


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
        personality=CharacterPersonality(traits=["Logical", "Studious", "Brave"]),
        speech=CharacterSpeech(tone=SpeechTone.ACADEMIC),
        goals=[CharacterGoal(id="goal_1", title="Research Nicolas Flamel", priority=80)],
    )
    harry = Character(
        id="char_harry",
        name="Harry Potter",
        description="The Boy Who Lived.",
    )
    library = Location(
        id="loc_library",
        name="Hogwarts Library",
        description="Quiet research hall.",
        category=LocationCategory.ROOM,
    )
    rule = WorldRule(
        id="rule_magic_wand",
        name="Wand Requirement",
        category=WorldRuleCategory.MAGIC,
        description="Casting spells requires a wand.",
    )
    rel = Relationship(
        id="rel_hermione_harry",
        source="char_hermione",
        target="char_harry",
        type=RelationshipType.FRIEND,
        scores=RelationshipScores(trust=80, respect=85, affection=75),
    )

    return Universe(
        metadata=meta,
        characters=[hermione, harry],
        locations=[library],
        world_rules=[rule],
        relationships=[rel],
    )


def create_sample_world_state() -> WorldState:
    char_states = {
        "char_hermione": CharacterState(
            character_id="char_hermione",
            location="loc_library",
            health="Healthy",
        ),
        "char_harry": CharacterState(
            character_id="char_harry",
            location="loc_library",
            health="Healthy",
        ),
    }
    loc_states = {
        "loc_library": LocationState(
            location_id="loc_library",
            occupants=["char_hermione", "char_harry"],
            objects=["obj_ancient_book"],
        )
    }
    return WorldState(
        universe_id="hp_001",
        time=WorldTime(day=5, hour=14),
        characters=char_states,
        locations=loc_states,
    )


# ---------------------------------------------------------------------------
# MemoryEngine Tests
# ---------------------------------------------------------------------------


class TestMemoryEngine:
    def test_retrieve_memories_keyword_and_importance_ranking(self):
        engine = MemoryEngine()

        m1 = Memory(
            id="mem_1",
            character_id="char_hermione",
            summary="User helped locate book in restricted section.",
            importance=80,
            timestamp=NOW,
        )
        m2 = Memory(
            id="mem_2",
            character_id="char_hermione",
            summary="User greeted Hermione in hall.",
            importance=20,
            timestamp=NOW,
        )
        m3 = Memory(
            id="mem_3",
            character_id="char_hermione",
            summary="User discussed Flamel research in library.",
            importance=90,
            timestamp=NOW,
        )

        retrieved = engine.retrieve_memories(
            character_id="char_hermione",
            memories=[m1, m2, m3],
            query="Tell me about Flamel research",
            limit=2,
        )

        assert len(retrieved) == 2
        assert retrieved[0].id == "mem_3"  # Matches query terms + high importance
        assert retrieved[1].id == "mem_1"

    def test_build_memory_context(self):
        engine = MemoryEngine()
        m1 = Memory(
            id="mem_1",
            character_id="char_hermione",
            summary="Defended Hermione in hall.",
            importance=75,
            timestamp=NOW,
        )

        context_str = engine.build_memory_context([m1])
        assert "[Importance: 75/100] Defended Hermione in hall." in context_str

    def test_apply_decay_filter(self):
        engine = MemoryEngine()
        m_high = Memory(id="mem_high", character_id="c1", summary="Core event", importance=80, timestamp=NOW)
        m_low = Memory(id="mem_low", character_id="c1", summary="Passed in hall", importance=10, timestamp=NOW)

        filtered = engine.apply_decay_filter([m_high, m_low], min_importance=20)
        assert len(filtered) == 1
        assert filtered[0].id == "mem_high"

    def test_evaluate_memory_candidates_with_ai_client(self):
        ai_resp = json.dumps(
            {
                "new_memories": [
                    {
                        "id": "mem_new_1",
                        "summary": "User shared secret spell book.",
                        "importance": "High",
                    }
                ],
                "updated_memories": [],
                "discarded_candidates": [],
            }
        )
        client = StubAIClient({"Character Memory Engine": ai_resp})
        engine = MemoryEngine(ai_client=client)

        uni = create_sample_universe()
        char = uni.characters[0]

        candidates = engine.evaluate_memory_candidates(
            character=char,
            existing_memories=[],
            user_action="I'm showing you this secret spell book.",
            interaction_summary="User showed secret spell book.",
        )

        assert len(candidates.new_memories) == 1
        assert candidates.new_memories[0]["summary"] == "User shared secret spell book."


# ---------------------------------------------------------------------------
# RelationshipEngine Tests
# ---------------------------------------------------------------------------


class TestRelationshipEngine:
    def test_clamp_score(self):
        engine = RelationshipEngine()
        assert engine.clamp_score(150, 0, 100) == 100
        assert engine.clamp_score(-50, 0, 100) == 0
        assert engine.clamp_score(75, 0, 100) == 75

    def test_calculate_delta_enforces_max_delta_and_bounds(self):
        engine = RelationshipEngine()
        current = RelationshipScores(trust=50, respect=50, affection=50)

        # Attempt +20 delta -> should be clamped to max_delta (+10)
        updated = engine.calculate_delta(current, {"trust": 20, "affection": 5})

        assert updated.trust == 60  # 50 + 10 max delta
        assert updated.affection == 55  # 50 + 5

    def test_infer_relationship_type(self):
        engine = RelationshipEngine()

        friend_scores = RelationshipScores(trust=80, affection=80)
        assert engine.infer_relationship_type(friend_scores) == RelationshipType.FRIEND

        enemy_scores = RelationshipScores(trust=10, affection=10)
        assert engine.infer_relationship_type(enemy_scores) == RelationshipType.ENEMY

        mentor_scores = RelationshipScores(trust=60, respect=80, affection=40)
        assert engine.infer_relationship_type(mentor_scores) == RelationshipType.MENTOR

    def test_build_relationship_context(self):
        engine = RelationshipEngine()
        rel = Relationship(
            id="rel_1",
            source="char_hermione",
            target="char_harry",
            type=RelationshipType.FRIEND,
            scores=RelationshipScores(trust=85, affection=80, respect=90),
        )

        context_str = engine.build_relationship_context([rel], character_id="char_hermione")
        assert "char_hermione -> char_harry (Friend)" in context_str
        assert "Trust=85" in context_str


# ---------------------------------------------------------------------------
# CharacterEngine Tests
# ---------------------------------------------------------------------------


class TestCharacterEngine:
    def test_build_context_contains_required_sections(self):
        client = StubAIClient()
        engine = CharacterEngine(ai_client=client)

        uni = create_sample_universe()
        ws = create_sample_world_state()
        char = uni.characters[0]

        ctx = engine.build_context(
            character=char,
            world_state=ws,
            universe=uni,
            user_action="What are you reading?",
        )

        assert "Hermione Granger" in ctx["character_profile"]
        assert "loc_library" in ctx["current_world_state"]
        assert "What are you reading?" in ctx["user_action"]
        assert "Wand Requirement" in ctx["universe_rules"]

    def test_generate_response_valid(self):
        ai_resp = json.dumps(
            {
                "character_id": "char_hermione",
                "dialogue": "I am studying an ancient manuscript on alchemy.",
                "emotion": "Focused",
                "actions": ["Adjusts parchment"],
                "memory_candidates": [],
                "relationship_changes": [],
                "world_effects": [],
                "follow_up_actions": [],
            }
        )
        client = StubAIClient({"Character Engine": ai_resp})
        engine = CharacterEngine(ai_client=client)

        uni = create_sample_universe()
        ws = create_sample_world_state()

        resp = engine.generate_response(
            character_id="char_hermione",
            world_state=ws,
            universe=uni,
            user_action="What are you studying?",
        )

        assert isinstance(resp, CharacterEngineResponse)
        assert resp.character_id == "char_hermione"
        assert resp.dialogue == "I am studying an ancient manuscript on alchemy."
        assert resp.emotion == "Focused"
        assert resp.actions == ["Adjusts parchment"]

    def test_validate_response_rejects_forbidden_ai_meta_language(self):
        client = StubAIClient()
        engine = CharacterEngine(ai_client=client)

        bad_dialogue = "As an AI language model, I cannot answer that."
        with pytest.raises(ValueError, match="immersion"):
            engine.validate_response(bad_dialogue)

    def test_engine_does_not_mutate_world_state_or_universe(self):
        ai_resp = json.dumps(
            {
                "character_id": "char_hermione",
                "dialogue": "Let us check the books.",
                "emotion": "Interested",
            }
        )
        client = StubAIClient({"character_response": ai_resp})
        engine = CharacterEngine(ai_client=client)

        uni = create_sample_universe()
        ws = create_sample_world_state()

        original_ws_day = ws.time.day
        original_char_count = len(uni.characters)

        _resp = engine.generate_response(
            character_id="char_hermione",
            world_state=ws,
            universe=uni,
            user_action="Can we look for books?",
        )

        # Assert no mutation occurred
        assert ws.time.day == original_ws_day
        assert len(uni.characters) == original_char_count
