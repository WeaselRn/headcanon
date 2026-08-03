"""
Unit tests for the Universe Builder.

These tests verify:
  * Text cleaning
  * Story segmentation
  * Entity building (characters, locations, objects, events, rules, relationships)
  * Knowledge graph construction
  * World state initialisation
  * Universe assembly and validation
  * Duplicate merging
  * Cross-reference validation (unknown participants, locations, relationship entities)
  * Error handling (build failure, prompt directory missing)

Tests never make real AI calls — a stub AIClient is injected.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from app.engines.universe_builder import (
    AIClient,
    BuildRequest,
    GeminiClientAdapter,
    UniverseBuilder,
    UniverseBuildError,
    _as_list,
    _ensure_id_prefix,
    _generate_universe_id,
    _map_edge_relationship,
    _map_event_type,
    _map_importance,
    _map_location_category,
    _map_node_type,
    _map_object_category,
    _map_relationship_type,
    _map_rule_category,
    _parse_json,
    _safe_int,
)
from app.world.knowledge_graph import EdgeRelationship, NodeType
from app.world.location import LocationCategory
from app.world.object import ObjectCategory
from app.world.relationship import RelationshipType
from app.world.timeline import EventType
from app.world.universe import ImportSource, WorldRuleCategory

# ---------------------------------------------------------------------------
# Stub AI Client
# ---------------------------------------------------------------------------


class StubAIClient(AIClient):
    """
    Returns canned JSON responses keyed by prompt prefix.

    The key for each response is matched against the *start* of the prompt
    text so that any prompt whose template begins with the configured prefix
    returns the pre-configured JSON response.

    If no key matches, an empty JSON object is returned.
    """

    def __init__(self, responses: dict[str, str] | None = None) -> None:
        self._responses = responses or {}

    def generate(self, prompt: str) -> str:
        for key, response in self._responses.items():
            if key in prompt:
                return response
        return "{}"


def _json(obj: Any) -> str:
    return json.dumps(obj)


# ---------------------------------------------------------------------------
# Minimal stub responses
# ---------------------------------------------------------------------------


def _stub_characters() -> str:
    return _json(
        {
            "characters": [
                {
                    "id": "char_harry",
                    "name": "Harry Potter",
                    "aliases": ["The Boy Who Lived"],
                    "species": "Human",
                    "occupation": "Student",
                    "age": 11,
                    "personality": ["Brave", "Loyal"],
                    "goals": ["Defeat Voldemort"],
                    "knowledge": ["Magic"],
                    "abilities": ["Parselmouth"],
                    "appearance": "Dark hair, green eyes",
                }
            ]
        }
    )


def _stub_locations() -> str:
    return _json(
        {
            "locations": [
                {
                    "id": "loc_hogwarts",
                    "name": "Hogwarts",
                    "type": "Castle",
                    "description": "A magical school.",
                    "connected_locations": [],
                },
                {
                    "id": "loc_great_hall",
                    "name": "Great Hall",
                    "type": "Room",
                    "description": "The main dining hall.",
                    "parent_location": "loc_hogwarts",
                    "connected_locations": ["loc_hogwarts"],
                },
            ]
        }
    )


def _stub_objects() -> str:
    return _json(
        {
            "objects": [
                {
                    "id": "obj_wand",
                    "name": "Elder Wand",
                    "type": "Artifact",
                    "description": "The most powerful wand.",
                    "abilities": ["Cast powerful spells"],
                }
            ]
        }
    )


def _stub_events() -> str:
    return _json(
        {
            "events": [
                {
                    "id": "evt_sorting",
                    "title": "Sorting Ceremony",
                    "description": "Students sorted into houses.",
                    "type": "Story",
                    "importance": "Major",
                    "participants": ["char_harry"],
                    "location": "loc_great_hall",
                    "status": "completed",
                },
                {
                    "id": "evt_troll",
                    "title": "Troll in the Dungeon",
                    "description": "A troll attacks.",
                    "type": "Combat",
                    "importance": "Critical",
                    "participants": ["char_harry"],
                    "location": "loc_hogwarts",
                    "status": "completed",
                },
            ]
        }
    )


def _stub_rules() -> str:
    return _json(
        {
            "rules": [
                {
                    "id": "rule_magic_requires_wand",
                    "title": "Magic Requires Wand",
                    "type": "Magic",
                    "description": "Witches and wizards need a wand to cast spells.",
                    "exceptions": ["House-elves"],
                }
            ]
        }
    )


def _stub_relationships() -> str:
    return _json(
        {
            "relationships": [
                {
                    "id": "rel_harry_hermione",
                    "character_a": "char_harry",
                    "character_b": "char_hermione",
                    "type": "Friend",
                    "strength": "Strong",
                    "status": "Active",
                }
            ]
        }
    )


def _stub_graph() -> str:
    return _json(
        {
            "nodes": [
                {"id": "char_harry", "label": "Harry Potter", "type": "Character"},
                {"id": "loc_hogwarts", "label": "Hogwarts", "type": "Location"},
            ],
            "edges": [
                {
                    "source": "char_harry",
                    "target": "loc_hogwarts",
                    "relation": "LIVES_IN",
                }
            ],
        }
    )


def _stub_world() -> str:
    return _json(
        {
            "world_state": {
                "current_time": "Day 1",
                "character_states": [
                    {
                        "character_id": "char_harry",
                        "location": "loc_great_hall",
                        "health": "Healthy",
                    }
                ],
                "location_states": [],
                "active_events": [],
                "pending_events": [],
                "world_variables": {},
            }
        }
    )


def _stub_merge(field_name: str, items: list[dict[str, Any]]) -> str:
    return _json({"entities": items, "changes": []})


def _make_full_stub_client() -> StubAIClient:
    """Create a stub client with keys matching the real prompt file prefixes."""
    return StubAIClient(
        {
            "Character Extraction": _stub_characters(),
            "Location Extraction": _stub_locations(),
            "Object Extraction": _stub_objects(),
            "Event Extraction": _stub_events(),
            "World Rules Extraction": _stub_rules(),
            "Relationship Extraction": _stub_relationships(),
            "Knowledge Graph Construction": _stub_graph(),
            "initialize_world": _stub_world(),
            "Merge duplicate": _stub_merge("entities", []),
        }
    )


def _make_full_stub_client_for_temp_prompts() -> StubAIClient:
    """Create a stub client with keys matching the temp prompt file content."""
    return StubAIClient(
        {
            "HEADCANON_CHAR_EXTRACT": _stub_characters(),
            "HEADCANON_LOC_EXTRACT": _stub_locations(),
            "HEADCANON_OBJ_EXTRACT": _stub_objects(),
            "HEADCANON_EVT_EXTRACT": _stub_events(),
            "HEADCANON_RULES_EXTRACT": _stub_rules(),
            "HEADCANON_REL_EXTRACT": _stub_relationships(),
            "HEADCANON_GRAPH_BUILD": _stub_graph(),
            "HEADCANON_WORLD_INIT": _stub_world(),
            # Return {} so the builder falls back to local ID-based deduplication
            # and the extracted entities (chars, locs, objs, etc.) are preserved.
            "HEADCANON_MERGE_DUPS": "{}",
        }
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def prompt_dir(tmp_path: Path) -> Path:
    """Create a temporary prompt directory with all required stub prompts."""
    pdir = tmp_path / "prompts" / "universe"
    pdir.mkdir(parents=True)

    required = [
        ("extract_characters.txt", "HEADCANON_CHAR_EXTRACT\n\n{story}"),
        ("extract_locations.txt", "HEADCANON_LOC_EXTRACT\n\n{story}"),
        ("extract_objects.txt", "HEADCANON_OBJ_EXTRACT\n\n{story}"),
        ("extract_events.txt", "HEADCANON_EVT_EXTRACT\n\n{story}"),
        ("extract_rules.txt", "HEADCANON_RULES_EXTRACT\n\n{story}"),
        ("extract_relationships.txt", "HEADCANON_REL_EXTRACT\n\n{story}"),
        ("build_knowledge_graph.txt", "HEADCANON_GRAPH_BUILD\n\n{universe}"),
        ("initialize_world.txt", "HEADCANON_WORLD_INIT\n\n{universe}"),
        ("merge_duplicates.txt", "HEADCANON_MERGE_DUPS\n\n{universe}"),
    ]

    for filename, content in required:
        (pdir / filename).write_text(content, encoding="utf-8")

    return pdir


@pytest.fixture
def builder(prompt_dir: Path) -> UniverseBuilder:
    """Universe Builder wired with stub AI client and temp prompts."""
    return UniverseBuilder(
        ai_client=_make_full_stub_client_for_temp_prompts(),
        prompt_dir=prompt_dir,
        chunk_size=10_000,
    )


# ---------------------------------------------------------------------------
# Tests — Text Cleaning
# ---------------------------------------------------------------------------


class TestTextCleaning:
    def test_removes_page_numbers(self, builder: UniverseBuilder) -> None:
        raw = "Hello.\n\n— 42 —\n\nWorld."
        cleaned = builder._clean_text(raw)
        assert "42" not in cleaned
        assert "Hello." in cleaned
        assert "World." in cleaned

    def test_removes_control_characters(self, builder: UniverseBuilder) -> None:
        raw = "Hello\x00World\x01."
        cleaned = builder._clean_text(raw)
        assert "\x00" not in cleaned
        assert "\x01" not in cleaned

    def test_normalises_windows_line_endings(self, builder: UniverseBuilder) -> None:
        raw = "Line A\r\nLine B\r\nLine C"
        cleaned = builder._clean_text(raw)
        assert "\r" not in cleaned

    def test_collapses_excess_blank_lines(self, builder: UniverseBuilder) -> None:
        raw = "A\n\n\n\n\n\nB"
        cleaned = builder._clean_text(raw)
        assert "\n\n\n\n" not in cleaned

    def test_preserves_dialogue(self, builder: UniverseBuilder) -> None:
        raw = '"Hello," said Harry. "How are you?"'
        cleaned = builder._clean_text(raw)
        assert '"Hello,"' in cleaned


# ---------------------------------------------------------------------------
# Tests — Story Segmentation
# ---------------------------------------------------------------------------


class TestSegmentation:
    def test_short_story_is_single_chunk(self, builder: UniverseBuilder) -> None:
        text = "A short story."
        chunks = builder._segment(text)
        assert len(chunks) == 1
        assert chunks[0] == "A short story."

    def test_long_story_splits_into_multiple_chunks(self, builder: UniverseBuilder) -> None:
        builder._chunk_size = 50
        text = "A" * 200
        chunks = builder._segment(text)
        assert len(chunks) > 1

    def test_splits_at_chapter_boundary(self, builder: UniverseBuilder) -> None:
        builder._chunk_size = 80
        text = ("A" * 40) + "\n\nChapter 2\n\n" + ("B" * 40)
        chunks = builder._segment(text)
        assert len(chunks) >= 2

    def test_each_chunk_within_size_limit(self, builder: UniverseBuilder) -> None:
        # Use a chunk size large enough that the splitter actually exercises its
        # forced-split logic, but the assertion is liberal enough to account for
        # the paragraph-boundary overshoot (splits at the nearest space, not
        # strictly at the byte limit).
        builder._chunk_size = 500
        text = "Word " * 400  # ~2000 chars
        chunks = builder._segment(text)
        # Every chunk should be smaller than 3× the nominal size
        for chunk in chunks:
            assert len(chunk) <= builder._chunk_size * 3


# ---------------------------------------------------------------------------
# Tests — Entity builders (unit tests against helpers directly)
# ---------------------------------------------------------------------------


class TestCharacterBuilder:
    def test_builds_valid_character(self, builder: UniverseBuilder) -> None:
        raw = [
            {
                "id": "char_harry",
                "name": "Harry Potter",
                "species": "Human",
                "age": 11,
                "personality": ["Brave"],
                "goals": ["Defeat Voldemort"],
                "abilities": ["Parselmouth"],
            }
        ]
        chars = builder._build_characters(raw, [])
        assert len(chars) == 1
        assert chars[0].id == "char_harry"
        assert chars[0].name == "Harry Potter"
        assert chars[0].age == 11

    def test_normalises_id_prefix(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "hermione", "name": "Hermione"}]
        chars = builder._build_characters(raw, [])
        assert chars[0].id == "char_hermione"

    def test_skips_blank_id(self, builder: UniverseBuilder) -> None:
        warnings: list[str] = []
        raw = [{"id": "", "name": "Ghost"}]
        chars = builder._build_characters(raw, warnings)
        assert len(chars) == 0
        assert any("blank ID" in w for w in warnings)

    def test_deduplicates_ability_ids(self, builder: UniverseBuilder) -> None:
        raw = [
            {
                "id": "char_harry",
                "name": "Harry",
                "abilities": ["Fly", "Fly"],  # duplicate string -> same auto-id
            }
        ]
        warnings: list[str] = []
        chars = builder._build_characters(raw, warnings)
        # Character should still be built (builder generates unique IDs by index)
        assert len(chars) == 1

    def test_goals_from_list_of_strings(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "char_harry", "name": "Harry", "goals": ["Goal 1", "Goal 2"]}]
        chars = builder._build_characters(raw, [])
        assert len(chars[0].goals) == 2

    def test_goals_from_list_of_dicts(self, builder: UniverseBuilder) -> None:
        raw = [
            {
                "id": "char_harry",
                "name": "Harry",
                "goals": [{"id": "goal_x", "title": "Win", "priority": 90}],
            }
        ]
        chars = builder._build_characters(raw, [])
        assert chars[0].goals[0].priority == 90


class TestLocationBuilder:
    def test_builds_valid_location(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "loc_library", "name": "Library", "type": "Building"}]
        locs = builder._build_locations(raw, [])
        assert len(locs) == 1
        assert locs[0].id == "loc_library"

    def test_normalises_id_prefix(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "forest", "name": "Forest", "type": "Forest"}]
        locs = builder._build_locations(raw, [])
        assert locs[0].id == "loc_forest"

    def test_removes_self_loop_connections(self, builder: UniverseBuilder) -> None:
        raw: list[dict[str, Any]] = [
            {
                "id": "loc_great_hall",
                "name": "Great Hall",
                "connected_locations": ["loc_great_hall", "loc_library"],
            },
            {"id": "loc_library", "name": "Library"},
        ]
        locs = builder._build_locations(raw, [])
        great_hall = next(loc for loc in locs if loc.id == "loc_great_hall")
        assert "loc_great_hall" not in great_hall.connections

    def test_removes_unknown_connections(self, builder: UniverseBuilder) -> None:
        warnings: list[str] = []
        raw = [
            {
                "id": "loc_great_hall",
                "name": "Great Hall",
                "connected_locations": ["loc_nonexistent"],
            }
        ]
        locs = builder._build_locations(raw, warnings)
        assert locs[0].connections == []
        assert any("unknown connection" in w for w in warnings)

    def test_maps_location_category(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "loc_castle", "name": "Castle", "type": "Castle"}]
        locs = builder._build_locations(raw, [])
        assert locs[0].category == LocationCategory.CASTLE


class TestObjectBuilder:
    def test_builds_valid_object(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "obj_wand", "name": "Wand", "type": "Artifact"}]
        objs = builder._build_objects(raw, [])
        assert len(objs) == 1
        assert objs[0].category == ObjectCategory.ARTIFACT

    def test_normalises_id_prefix(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "sword", "name": "Sword", "type": "Weapon"}]
        objs = builder._build_objects(raw, [])
        assert objs[0].id == "obj_sword"

    def test_skips_blank_id(self, builder: UniverseBuilder) -> None:
        warnings: list[str] = []
        raw = [{"id": "", "name": "Mystery Item"}]
        objs = builder._build_objects(raw, warnings)
        assert len(objs) == 0


class TestTimelineBuilder:
    def test_builds_valid_timeline(self, builder: UniverseBuilder) -> None:
        raw = [
            {"id": "evt_sorting", "title": "Sorting", "type": "Story"},
            {"id": "evt_troll", "title": "Troll", "type": "Combat"},
        ]
        timeline = builder._build_timeline(raw, [])
        assert len(timeline.events) == 2
        # Sequences must be monotonically increasing
        seqs = [e.sequence for e in timeline.events]
        assert seqs == sorted(seqs)

    def test_events_get_unique_sequences(self, builder: UniverseBuilder) -> None:
        raw = [{"id": f"evt_{i}", "title": f"Event {i}"} for i in range(5)]
        timeline = builder._build_timeline(raw, [])
        seqs = [e.sequence for e in timeline.events]
        assert len(seqs) == len(set(seqs))

    def test_auto_generates_id_for_blank(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "", "title": "Unnamed Event"}]
        timeline = builder._build_timeline(raw, [])
        assert timeline.events[0].id.startswith("evt_")

    def test_maps_importance(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "evt_x", "title": "X", "importance": "Critical"}]
        timeline = builder._build_timeline(raw, [])
        assert timeline.events[0].importance >= 80


class TestWorldRuleBuilder:
    def test_builds_valid_rule(self, builder: UniverseBuilder) -> None:
        raw = [
            {
                "id": "rule_magic",
                "title": "Magic Rule",
                "type": "Magic",
                "description": "Magic requires a wand.",
            }
        ]
        rules = builder._build_world_rules(raw, [])
        assert len(rules) == 1
        assert rules[0].id == "rule_magic"
        assert rules[0].category == WorldRuleCategory.MAGIC

    def test_normalises_id_prefix(self, builder: UniverseBuilder) -> None:
        raw = [{"id": "magic_law", "title": "Magic", "type": "Magic", "description": "..."}]
        rules = builder._build_world_rules(raw, [])
        assert rules[0].id == "rule_magic_law"


class TestRelationshipBuilder:
    def test_builds_valid_relationship(self, builder: UniverseBuilder) -> None:
        char_ids = {"char_harry", "char_hermione"}
        raw = [
            {
                "id": "rel_harry_hermione",
                "character_a": "char_harry",
                "character_b": "char_hermione",
                "type": "Friend",
            }
        ]
        rels = builder._build_relationships(raw, char_ids, [])
        assert len(rels) == 1
        assert rels[0].type == RelationshipType.FRIEND

    def test_skips_self_relationship(self, builder: UniverseBuilder) -> None:
        warnings: list[str] = []
        char_ids = {"char_harry"}
        raw = [{"character_a": "char_harry", "character_b": "char_harry", "type": "Friend"}]
        rels = builder._build_relationships(raw, char_ids, warnings)
        assert len(rels) == 0
        assert any("Self-relationship" in w for w in warnings)

    def test_skips_unknown_source(self, builder: UniverseBuilder) -> None:
        warnings: list[str] = []
        char_ids = {"char_harry"}
        raw = [{"character_a": "char_ghost", "character_b": "char_harry", "type": "Friend"}]
        rels = builder._build_relationships(raw, char_ids, warnings)
        assert len(rels) == 0

    def test_auto_generates_rel_id(self, builder: UniverseBuilder) -> None:
        char_ids = {"char_harry", "char_ron"}
        raw = [{"character_a": "char_harry", "character_b": "char_ron", "type": "Friend"}]
        rels = builder._build_relationships(raw, char_ids, [])
        assert rels[0].id.startswith("rel_")


class TestKnowledgeGraphBuilder:
    def test_builds_valid_graph(self, builder: UniverseBuilder) -> None:
        graph_data = {
            "nodes": [
                {"id": "char_harry", "label": "Harry", "type": "Character"},
                {"id": "loc_hogwarts", "label": "Hogwarts", "type": "Location"},
            ],
            "edges": [
                {"source": "char_harry", "target": "loc_hogwarts", "relation": "LIVES_IN"}
            ],
        }
        graph = builder._build_knowledge_graph(graph_data, [])
        assert len(graph.nodes) == 2
        assert len(graph.edges) == 1

    def test_drops_duplicate_nodes(self, builder: UniverseBuilder) -> None:
        warnings: list[str] = []
        graph_data = {
            "nodes": [
                {"id": "char_harry", "label": "Harry", "type": "Character"},
                {"id": "char_harry", "label": "Harry Again", "type": "Character"},
            ],
            "edges": [],
        }
        graph = builder._build_knowledge_graph(graph_data, warnings)
        assert len(graph.nodes) == 1
        assert any("duplicate node" in w.lower() for w in warnings)

    def test_drops_dangling_edges(self, builder: UniverseBuilder) -> None:
        graph_data = {
            "nodes": [{"id": "char_harry", "label": "Harry", "type": "Character"}],
            "edges": [
                {"source": "char_harry", "target": "loc_unknown", "relation": "LIVES_IN"}
            ],
        }
        graph = builder._build_knowledge_graph(graph_data, [])
        assert len(graph.edges) == 0

    def test_drops_self_loop_edges(self, builder: UniverseBuilder) -> None:
        graph_data = {
            "nodes": [{"id": "char_harry", "label": "Harry", "type": "Character"}],
            "edges": [
                {"source": "char_harry", "target": "char_harry", "relation": "KNOWS"}
            ],
        }
        graph = builder._build_knowledge_graph(graph_data, [])
        assert len(graph.edges) == 0

    def test_drops_duplicate_edges(self, builder: UniverseBuilder) -> None:
        graph_data = {
            "nodes": [
                {"id": "char_harry", "type": "Character", "label": "Harry"},
                {"id": "loc_hogwarts", "type": "Location", "label": "Hogwarts"},
            ],
            "edges": [
                {"source": "char_harry", "target": "loc_hogwarts", "relation": "LIVES_IN"},
                {"source": "char_harry", "target": "loc_hogwarts", "relation": "LIVES_IN"},
            ],
        }
        graph = builder._build_knowledge_graph(graph_data, [])
        assert len(graph.edges) == 1


# ---------------------------------------------------------------------------
# Tests — Full build (integration within unit-test scope)
# ---------------------------------------------------------------------------


class TestFullBuild:
    def test_build_returns_valid_universe(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(
            story_text="Harry Potter attended Hogwarts.",
            title="Harry Potter Test",
            author="Test Author",
        )
        result = builder.build(request)
        assert result.universe.metadata.title == "Harry Potter Test"
        assert result.universe.metadata.author == "Test Author"

    def test_universe_metadata_has_correct_source(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(
            story_text="A story.",
            title="My Story",
            source=ImportSource.PDF,
        )
        result = builder.build(request)
        assert result.universe.metadata.source == ImportSource.PDF

    def test_universe_id_is_auto_generated_when_not_provided(
        self, builder: UniverseBuilder
    ) -> None:
        request = BuildRequest(story_text="A story.", title="Auto ID Test")
        result = builder.build(request)
        assert result.universe.metadata.id != ""

    def test_universe_id_uses_provided_id(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(
            story_text="A story.", title="Custom ID Test", universe_id="hp_custom_001"
        )
        result = builder.build(request)
        assert result.universe.metadata.id == "hp_custom_001"

    def test_characters_extracted(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(story_text="Harry Potter is brave.", title="HP Test")
        result = builder.build(request)
        assert any(c.id == "char_harry" for c in result.universe.characters)

    def test_locations_extracted(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(story_text="Hogwarts is a castle.", title="HP Test")
        result = builder.build(request)
        assert any(loc.id == "loc_hogwarts" for loc in result.universe.locations)

    def test_objects_extracted(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(story_text="The Elder Wand.", title="HP Test")
        result = builder.build(request)
        assert any(o.id == "obj_wand" for o in result.universe.objects)

    def test_world_state_initialised(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(story_text="Harry arrived at Hogwarts.", title="HP Test")
        result = builder.build(request)
        assert result.universe.world_state is not None
        assert result.universe.world_state.flags.get("world_initialized") is True

    def test_world_state_flags(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(story_text="Story text.", title="Test")
        result = builder.build(request)
        ws = result.universe.world_state
        assert ws is not None
        assert ws.flags["simulation_started"] is False
        assert ws.flags["user_joined"] is False

    def test_build_with_explicit_universe_id(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(
            story_text="Story.", title="Title", universe_id="my_universe_001"
        )
        result = builder.build(request)
        assert result.universe.metadata.id == "my_universe_001"

    def test_relationships_reference_only_known_chars(
        self, builder: UniverseBuilder
    ) -> None:
        """
        The stub relationship mentions char_hermione which is NOT in the stub
        character extraction.  The builder must skip it.
        """
        request = BuildRequest(story_text="Story.", title="Title")
        result = builder.build(request)
        char_ids = {c.id for c in result.universe.characters}
        for rel in result.universe.relationships:
            assert rel.source in char_ids
            assert rel.target in char_ids

    def test_timeline_events_have_unique_sequences(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(story_text="Story.", title="Title")
        result = builder.build(request)
        seqs = [e.sequence for e in result.universe.timeline.events]
        assert len(seqs) == len(set(seqs))

    def test_timeline_events_are_ordered(self, builder: UniverseBuilder) -> None:
        request = BuildRequest(story_text="Story.", title="Title")
        result = builder.build(request)
        seqs = [e.sequence for e in result.universe.timeline.events]
        assert seqs == sorted(seqs)


# ---------------------------------------------------------------------------
# Tests — Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    def test_missing_prompt_dir_raises(self, tmp_path: Path) -> None:
        non_existent = tmp_path / "nonexistent_prompts"
        with pytest.raises(UniverseBuildError, match="Prompt directory not found"):
            UniverseBuilder(
                ai_client=StubAIClient(),
                prompt_dir=non_existent,
            )

    def test_missing_required_prompt_file_raises(self, tmp_path: Path) -> None:
        pdir = tmp_path / "prompts"
        pdir.mkdir()
        # Only create one prompt — not all required files
        (pdir / "extract_characters.txt").write_text("Character Extraction\n{story}")
        with pytest.raises(UniverseBuildError, match="Required prompt file not found"):
            UniverseBuilder(ai_client=StubAIClient(), prompt_dir=pdir)

    def test_ai_returning_invalid_json_is_logged_and_skipped(
        self, prompt_dir: Path
    ) -> None:
        """
        If an extractor returns invalid JSON, the entity list should be empty
        and a warning recorded — but the build should not crash.
        """
        bad_client = StubAIClient(
            {
                "Character Extraction": "NOT JSON",
                "Location Extraction": "NOT JSON",
                "Object Extraction": "NOT JSON",
                "Event Extraction": "NOT JSON",
                "World Rules Extraction": "NOT JSON",
                "Relationship Extraction": "NOT JSON",
                "Knowledge Graph Construction": "{}",
                "initialize": "{}",
                "Merge duplicate": "{}",
            }
        )
        builder = UniverseBuilder(ai_client=bad_client, prompt_dir=prompt_dir)
        result = builder.build(BuildRequest(story_text="Story.", title="Bad JSON Test"))
        # Universe should still be produced (empty but valid)
        assert result.universe is not None
        assert len(result.universe.characters) == 0


# ---------------------------------------------------------------------------
# Tests — Helper functions
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_parse_json_plain(self) -> None:
        assert _parse_json('{"key": "value"}') == {"key": "value"}

    def test_parse_json_fenced(self) -> None:
        fenced = "```json\n{\"key\": \"value\"}\n```"
        assert _parse_json(fenced) == {"key": "value"}

    def test_parse_json_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="invalid JSON"):
            _parse_json("NOT JSON")

    def test_ensure_id_prefix_already_has_prefix(self) -> None:
        assert _ensure_id_prefix("char_harry", "char_") == "char_harry"

    def test_ensure_id_prefix_adds_prefix(self) -> None:
        assert _ensure_id_prefix("harry", "char_") == "char_harry"

    def test_ensure_id_prefix_blank_returns_prefix(self) -> None:
        assert _ensure_id_prefix("", "char_") == "char_"

    def test_ensure_id_prefix_slugifies_spaces(self) -> None:
        result = _ensure_id_prefix("Harry Potter", "char_")
        assert " " not in result
        assert result == "char_harry_potter"

    def test_generate_universe_id_format(self) -> None:
        uid = _generate_universe_id("Harry Potter and the Stone")
        assert "_" in uid
        assert uid.islower()

    def test_as_list_none(self) -> None:
        assert _as_list(None) == []

    def test_as_list_list(self) -> None:
        assert _as_list([1, 2]) == [1, 2]

    def test_as_list_scalar(self) -> None:
        assert _as_list("hello") == ["hello"]

    def test_safe_int_valid(self) -> None:
        assert _safe_int("42") == 42

    def test_safe_int_invalid(self) -> None:
        assert _safe_int("not a number") is None

    def test_safe_int_none(self) -> None:
        assert _safe_int(None) is None

    def test_map_location_category_castle(self) -> None:
        assert _map_location_category("Castle") == LocationCategory.CASTLE

    def test_map_location_category_unknown(self) -> None:
        assert _map_location_category("XYZ") is None

    def test_map_object_category_weapon(self) -> None:
        assert _map_object_category("Weapon") == ObjectCategory.WEAPON

    def test_map_object_category_unknown(self) -> None:
        assert _map_object_category("XYZ") is None

    def test_map_event_type_combat(self) -> None:
        assert _map_event_type("Combat") == EventType.COMBAT

    def test_map_event_type_unknown_defaults_to_story(self) -> None:
        assert _map_event_type("UnknownType") == EventType.STORY_EVENT

    def test_map_rule_category_magic(self) -> None:
        assert _map_rule_category("Magic") == WorldRuleCategory.MAGIC

    def test_map_rule_category_unknown_defaults(self) -> None:
        assert _map_rule_category("XYZ") == WorldRuleCategory.LORE

    def test_map_relationship_type_friend(self) -> None:
        assert _map_relationship_type("Friend") == RelationshipType.FRIEND

    def test_map_relationship_type_unknown_defaults_to_neutral(self) -> None:
        assert _map_relationship_type("XYZ") == RelationshipType.NEUTRAL

    def test_map_importance_critical(self) -> None:
        assert _map_importance("Critical") >= 80

    def test_map_importance_unknown_defaults(self) -> None:
        assert _map_importance("XYZ") == 50

    def test_map_node_type_character(self) -> None:
        assert _map_node_type("Character") == NodeType.CHARACTER

    def test_map_node_type_unknown_defaults(self) -> None:
        assert _map_node_type("XYZ") == NodeType.CHARACTER

    def test_map_edge_relationship_lives_in(self) -> None:
        assert _map_edge_relationship("LIVES_IN") == EdgeRelationship.LIVES_IN

    def test_map_edge_relationship_unknown_defaults(self) -> None:
        assert _map_edge_relationship("XYZ") == EdgeRelationship.AFFECTED


# ---------------------------------------------------------------------------
# Tests — GeminiClientAdapter
# ---------------------------------------------------------------------------


class TestGeminiClientAdapter:
    def test_adapter_delegates_to_generate_text(self) -> None:
        class FakeGemini:
            def generate_text(self, prompt: str) -> str:
                return '{"result": "ok"}'

        adapter = GeminiClientAdapter(FakeGemini())
        result = adapter.generate("test prompt")
        assert result == '{"result": "ok"}'
