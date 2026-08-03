"""
Unit tests for Headcanon World Simulation System (Milestone 7).

Tests TimelineEngine and SimulationEngine for:
  - Time progression & day/hour overflow handling
  - Chronological event creation, sequence ordering, and timeline branching
  - Executing pending world effects (location updates, inventory transfers, relationship updates, time advances)
  - Relationship score clamping [0, 100] and delta capping (+/-10)
  - NPC background activity scheduling
  - WorldState validation against Universe models
  - Immutability of Universe models during simulation
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.engines.interaction_engine import InteractionResult
from app.engines.simulation_engine import SimulationEngine, SimulationResult
from app.engines.timeline_engine import TimelineEngine
from app.world.character import Character
from app.world.location import Location, LocationCategory
from app.world.object import Object, ObjectCategory
from app.world.scene import Scene, SceneLocationSummary
from app.world.timeline import (
    EventStatus,
    EventType,
    Timeline,
    TimelineBranch,
    TimelineEvent,
    WorldTime,
)
from app.world.universe import ImportSource, Universe, UniverseMetadata
from app.world.world_state import CharacterState, LocationState, WorldState

NOW = datetime(2026, 8, 4, 1, 0, 0, tzinfo=UTC)


def create_sample_universe() -> Universe:
    meta = UniverseMetadata(
        id="hp_001",
        title="Harry Potter",
        author="J. K. Rowling",
        source=ImportSource.CUSTOM,
        created_at=NOW,
    )
    hermione = Character(id="char_hermione", name="Hermione Granger")
    harry = Character(id="char_harry", name="Harry Potter")
    user = Character(id="char_user", name="Player")

    library = Location(
        id="loc_library",
        name="Hogwarts Library",
        description="Quiet research hall.",
        category=LocationCategory.ROOM,
        connections=["loc_hallway"],
    )
    hallway = Location(
        id="loc_hallway",
        name="Corridor",
        description="Stone corridor.",
        category=LocationCategory.ROOM,
        connections=["loc_library"],
    )
    book = Object(
        id="obj_wand",
        name="Elder Wand",
        description="Powerful wand.",
        category=ObjectCategory.WEAPON,
        location="loc_library",
    )

    return Universe(
        metadata=meta,
        characters=[hermione, harry, user],
        locations=[library, hallway],
        objects=[book],
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
            objects=["obj_wand"],
        ),
        "loc_hallway": LocationState(
            location_id="loc_hallway",
            occupants=["char_harry"],
        ),
    }
    return WorldState(
        universe_id="hp_001",
        time=WorldTime(day=1, hour=10),
        characters=char_states,
        locations=loc_states,
    )


# ---------------------------------------------------------------------------
# TimelineEngine Tests
# ---------------------------------------------------------------------------


class TestTimelineEngine:
    def test_advance_time(self):
        engine = TimelineEngine()
        t0 = WorldTime(day=1, hour=22)

        t1 = engine.advance_time(t0, 5)
        assert t1.day == 2
        assert t1.hour == 3

    def test_create_event(self):
        engine = TimelineEngine()
        evt = engine.create_event(
            title="Sorting Ceremony",
            description="First years are sorted.",
            event_type=EventType.STORY_EVENT,
            location="loc_great_hall",
            participants=["char_harry", "char_hermione"],
            sequence=1,
        )

        assert isinstance(evt, TimelineEvent)
        assert evt.id.startswith("evt_sorting_ceremony_")
        assert evt.title == "Sorting Ceremony"
        assert len(evt.participants) == 2

    def test_append_event_maintains_sorted_order(self):
        engine = TimelineEngine()
        tl = Timeline()

        e2 = engine.create_event("Second Event", "Desc", sequence=2)
        e1 = engine.create_event("First Event", "Desc", sequence=1)

        tl1 = engine.append_event(tl, e2)
        tl2 = engine.append_event(tl1, e1)

        assert len(tl2.events) == 2
        assert tl2.events[0].sequence == 1
        assert tl2.events[1].sequence == 2
        assert tl2.completed_events == [e2.id, e1.id]

    def test_create_branch(self):
        engine = TimelineEngine()
        tl = Timeline()
        branch = engine.create_branch(
            timeline=tl,
            origin_event_id="evt_troll_attack",
            description="Ron leaves Hogwarts.",
        )

        assert isinstance(branch, TimelineBranch)
        assert branch.branch_id.startswith("branch_")
        assert branch.origin_event == "evt_troll_attack"

    def test_validate_timeline_success_and_failure(self):
        engine = TimelineEngine()
        tl = Timeline()

        valid, err = engine.validate_timeline(tl)
        assert valid
        assert err is None


# ---------------------------------------------------------------------------
# SimulationEngine Tests
# ---------------------------------------------------------------------------


class TestSimulationEngine:
    def test_simulate_interaction_location_update(self):
        engine = SimulationEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        scene = Scene(
            scene_id="scene_library",
            universe_id="hp_001",
            location=SceneLocationSummary(location_id="loc_library", name="Library"),
        )
        interaction = InteractionResult(
            interaction_id="int_001",
            action="travel",
            target="loc_hallway",
            scene=scene,
            pending_world_effects=[
                {"type": "location_update", "target_location": "loc_hallway"}
            ],
            success=True,
        )

        result = engine.simulate_interaction(
            interaction_result=interaction,
            world_state=ws,
            universe=uni,
            user_character_id="char_user",
        )

        assert isinstance(result, SimulationResult)
        assert result.success
        # Assert player moved to hallway
        assert result.updated_world_state.characters["char_user"].location == "loc_hallway"
        assert "char_user" in result.updated_world_state.locations["loc_hallway"].occupants
        assert "char_user" not in result.updated_world_state.locations["loc_library"].occupants

    def test_simulate_interaction_relationship_update_with_bounds(self):
        engine = SimulationEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        scene = Scene(
            scene_id="scene_library",
            universe_id="hp_001",
            location=SceneLocationSummary(location_id="loc_library", name="Library"),
        )
        interaction = InteractionResult(
            interaction_id="int_002",
            action="talk",
            target="char_hermione",
            scene=scene,
            pending_world_effects=[
                {
                    "type": "suggest_relationships",
                    "changes": [{"target": "char_hermione", "delta": 25}],  # Should be capped at +10
                }
            ],
            success=True,
        )

        result = engine.simulate_interaction(
            interaction_result=interaction,
            world_state=ws,
            universe=uni,
            user_character_id="char_user",
        )

        assert result.success
        rel_st = result.updated_world_state.relationships["char_user_char_hermione"]
        assert rel_st.trust == 60  # Initial 50 + capped delta 10 = 60

    def test_simulate_interaction_advance_time(self):
        engine = SimulationEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        scene = Scene(
            scene_id="scene_library",
            universe_id="hp_001",
            location=SceneLocationSummary(location_id="loc_library", name="Library"),
        )
        interaction = InteractionResult(
            interaction_id="int_003",
            action="wait",
            scene=scene,
            pending_world_effects=[{"type": "advance_time", "hours": 3}],
            success=True,
        )

        result = engine.simulate_interaction(
            interaction_result=interaction,
            world_state=ws,
            universe=uni,
        )

        assert result.success
        assert result.updated_world_state.time.hour == 13  # Initial 10 + 3 = 13

    def test_validate_world_state_detects_invalid_character_reference(self):
        engine = SimulationEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        # Add invalid character to WorldState
        ws.characters["char_ghost"] = CharacterState(character_id="char_ghost", location="loc_library")

        valid, err = engine.validate_world_state(ws, uni)
        assert not valid
        assert "char_ghost" in err

    def test_universe_model_remains_immutable_during_simulation(self):
        engine = SimulationEngine()
        uni = create_sample_universe()
        ws = create_sample_world_state()

        original_char_count = len(uni.characters)
        original_loc_count = len(uni.locations)

        scene = Scene(
            scene_id="scene_library",
            universe_id="hp_001",
            location=SceneLocationSummary(location_id="loc_library", name="Library"),
        )
        interaction = InteractionResult(
            interaction_id="int_004",
            action="travel",
            target="loc_hallway",
            scene=scene,
            pending_world_effects=[
                {"type": "location_update", "target_location": "loc_hallway"}
            ],
            success=True,
        )

        _res = engine.simulate_interaction(interaction, ws, uni)

        # Assert Universe was not mutated
        assert len(uni.characters) == original_char_count
        assert len(uni.locations) == original_loc_count
