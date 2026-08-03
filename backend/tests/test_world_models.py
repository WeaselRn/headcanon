"""
Smoke tests for the canonical world data models.

These tests verify that every model in ``app.world`` can be instantiated,
validates correctly, serialises to JSON, and rejects invalid data.

They do NOT test any engine logic, AI behaviour, or storage.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.world.character import (
    Character,
    CharacterAbility,
    CharacterPersonality,
    EntityMetadata,
)
from app.world.emotion import EmotionCategory, EmotionState
from app.world.inventory import Inventory, InventoryItem, InventoryType
from app.world.knowledge_graph import (
    EdgeRelationship,
    GraphEdge,
    GraphNode,
    KnowledgeGraph,
    NodeType,
)
from app.world.location import Location, LocationCategory
from app.world.memory import Memory, MemoryType
from app.world.object import Object, ObjectCategory
from app.world.relationship import Relationship, RelationshipScores, RelationshipType
from app.world.scene import Scene, SceneLocationSummary, SceneMetadata
from app.world.snapshot import Snapshot, SnapshotMetadata, SnapshotSaveType, SnapshotVersionMetadata
from app.world.timeline import EventStatus, Timeline, TimelineEvent, WorldTime
from app.world.universe import (
    ImportSource,
    Universe,
    UniverseMetadata,
    WorldRule,
    WorldRuleCategory,
)
from app.world.world_state import CharacterState, ObjectState, WorldState

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NOW = datetime(2026, 8, 1, 9, 0, 0, tzinfo=UTC)


def minimal_character(char_id: str = "char_harry") -> Character:
    return Character(
        id=char_id,
        name="Harry Potter",
        description="The Boy Who Lived.",
    )


def minimal_location(loc_id: str = "loc_great_hall") -> Location:
    return Location(
        id=loc_id,
        name="Great Hall",
        description="A vast dining hall.",
        category=LocationCategory.ROOM,
    )


def minimal_object(obj_id: str = "obj_wand") -> Object:
    return Object(
        id=obj_id,
        name="Elder Wand",
        category=ObjectCategory.MAGIC_ITEM,
        description="The most powerful wand ever created.",
    )


def minimal_event(seq: int = 1) -> TimelineEvent:
    return TimelineEvent(
        id="evt_sorting",
        title="Sorting Ceremony",
        sequence=seq,
        status=EventStatus.COMPLETED,
    )


def minimal_universe_metadata() -> UniverseMetadata:
    return UniverseMetadata(
        id="hp_001",
        title="Harry Potter and the Philosopher's Stone",
        author="J. K. Rowling",
        source=ImportSource.PDF,
        created_at=NOW,
    )


# ---------------------------------------------------------------------------
# Character tests
# ---------------------------------------------------------------------------


class TestCharacter:
    def test_valid_character(self):
        char = minimal_character()
        assert char.id == "char_harry"
        assert char.name == "Harry Potter"

    def test_id_pattern_enforced(self):
        with pytest.raises(Exception):
            Character(id="harry", name="Harry")

    def test_duplicate_aliases_rejected(self):
        with pytest.raises(Exception):
            Character(id="char_harry", name="Harry", aliases=["H", "H"])

    def test_duplicate_abilities_rejected(self):
        ability = CharacterAbility(id="spell_x", name="X", description="X spell")
        with pytest.raises(Exception):
            Character(id="char_harry", name="Harry", abilities=[ability, ability])

    def test_self_reference_in_knowledge_rejected(self):
        from app.world.character import CharacterKnowledge
        knowledge = CharacterKnowledge(known_people=["char_harry"])
        with pytest.raises(Exception):
            Character(id="char_harry", name="Harry", knowledge=knowledge)

    def test_json_serialisable(self):
        char = minimal_character()
        data = char.model_dump_json()
        assert "Harry Potter" in data

    def test_personality_immutable(self):
        personality = CharacterPersonality(traits=["Brave"])
        with pytest.raises(Exception):
            personality.traits = ["Cowardly"]  # type: ignore[misc]

    def test_metadata_confidence_range(self):
        with pytest.raises(Exception):
            EntityMetadata(confidence=1.5)

    def test_metadata_importance_range(self):
        with pytest.raises(Exception):
            EntityMetadata(importance=0)


# ---------------------------------------------------------------------------
# Location tests
# ---------------------------------------------------------------------------


class TestLocation:
    def test_valid_location(self):
        loc = minimal_location()
        assert loc.id == "loc_great_hall"
        assert loc.category == LocationCategory.ROOM

    def test_id_pattern_enforced(self):
        with pytest.raises(Exception):
            Location(id="great_hall", name="Great Hall")

    def test_duplicate_connections_rejected(self):
        with pytest.raises(Exception):
            Location(
                id="loc_great_hall",
                name="Great Hall",
                connections=["loc_library", "loc_library"],
            )

    def test_non_loc_connection_rejected(self):
        with pytest.raises(Exception):
            Location(
                id="loc_great_hall",
                name="Great Hall",
                connections=["char_harry"],
            )

    def test_json_serialisable(self):
        data = minimal_location().model_dump_json()
        assert "Great Hall" in data


# ---------------------------------------------------------------------------
# Object tests
# ---------------------------------------------------------------------------


class TestObject:
    def test_valid_object(self):
        obj = minimal_object()
        assert obj.id == "obj_wand"

    def test_id_pattern_enforced(self):
        with pytest.raises(Exception):
            Object(id="wand", name="Wand")

    def test_json_serialisable(self):
        data = minimal_object().model_dump_json()
        assert "Elder Wand" in data


# ---------------------------------------------------------------------------
# Relationship tests
# ---------------------------------------------------------------------------


class TestRelationship:
    def test_valid_relationship(self):
        rel = Relationship(
            id="rel_harry_hermione",
            source="char_harry",
            target="char_hermione",
            type=RelationshipType.FRIEND,
        )
        assert rel.scores.trust == 50

    def test_self_relationship_rejected(self):
        with pytest.raises(Exception):
            Relationship(
                id="rel_harry_harry",
                source="char_harry",
                target="char_harry",
            )

    def test_score_bounds(self):
        with pytest.raises(Exception):
            RelationshipScores(trust=101)

    def test_json_serialisable(self):
        rel = Relationship(
            id="rel_harry_hermione",
            source="char_harry",
            target="char_hermione",
        )
        data = rel.model_dump_json()
        assert "char_harry" in data


# ---------------------------------------------------------------------------
# Timeline tests
# ---------------------------------------------------------------------------


class TestTimeline:
    def test_valid_timeline(self):
        events = [
            TimelineEvent(id="evt_sorting", title="Sorting", sequence=1),
            TimelineEvent(id="evt_troll", title="Troll Attack", sequence=2),
        ]
        tl = Timeline(events=events)
        assert len(tl.events) == 2

    def test_duplicate_sequences_rejected(self):
        events = [
            TimelineEvent(id="evt_sorting", title="Sorting", sequence=1),
            TimelineEvent(id="evt_troll", title="Troll", sequence=1),
        ]
        with pytest.raises(Exception):
            Timeline(events=events)

    def test_unordered_sequences_rejected(self):
        events = [
            TimelineEvent(id="evt_troll", title="Troll", sequence=5),
            TimelineEvent(id="evt_sorting", title="Sorting", sequence=1),
        ]
        with pytest.raises(Exception):
            Timeline(events=events)

    def test_world_time_defaults(self):
        wt = WorldTime()
        assert wt.day == 1
        assert wt.hour == 0


# ---------------------------------------------------------------------------
# Knowledge Graph tests
# ---------------------------------------------------------------------------


class TestKnowledgeGraph:
    def test_valid_graph(self):
        harry = GraphNode(id="char_harry", type=NodeType.CHARACTER, name="Harry")
        wand = GraphNode(id="obj_wand", type=NodeType.OBJECT, name="Wand")
        edge = GraphEdge(
            source="char_harry",
            target="obj_wand",
            relationship=EdgeRelationship.OWNS,
        )
        graph = KnowledgeGraph(nodes=[harry, wand], edges=[edge])
        assert len(graph.nodes) == 2

    def test_duplicate_node_ids_rejected(self):
        harry = GraphNode(id="char_harry", type=NodeType.CHARACTER, name="Harry")
        with pytest.raises(Exception):
            KnowledgeGraph(nodes=[harry, harry])

    def test_dangling_edge_rejected(self):
        harry = GraphNode(id="char_harry", type=NodeType.CHARACTER, name="Harry")
        edge = GraphEdge(
            source="char_harry",
            target="obj_nonexistent",
            relationship=EdgeRelationship.OWNS,
        )
        with pytest.raises(Exception):
            KnowledgeGraph(nodes=[harry], edges=[edge])

    def test_self_loop_rejected(self):
        with pytest.raises(Exception):
            GraphEdge(
                source="char_harry",
                target="char_harry",
                relationship=EdgeRelationship.KNOWS,
            )


# ---------------------------------------------------------------------------
# World State tests
# ---------------------------------------------------------------------------


class TestWorldState:
    def test_valid_world_state(self):
        ws = WorldState(universe_id="hp_001")
        assert ws.universe_id == "hp_001"

    def test_character_state(self):
        cs = CharacterState(character_id="char_harry", location="loc_great_hall")
        assert cs.health == "Healthy"

    def test_object_state(self):
        os_ = ObjectState(object_id="obj_wand", owner="char_harry")
        assert os_.hidden is False

    def test_json_serialisable(self):
        ws = WorldState(universe_id="hp_001")
        data = ws.model_dump_json()
        assert "hp_001" in data


# ---------------------------------------------------------------------------
# Inventory tests
# ---------------------------------------------------------------------------


class TestInventory:
    def test_valid_inventory(self):
        item = InventoryItem(item_id="obj_wand", name="Wand")
        inv = Inventory(
            inventory_id="inv_harry",
            owner_id="char_harry",
            type=InventoryType.CHARACTER,
            items=[item],
        )
        assert len(inv.items) == 1

    def test_duplicate_item_rejected(self):
        item = InventoryItem(item_id="obj_wand", name="Wand")
        with pytest.raises(Exception):
            Inventory(
                inventory_id="inv_harry",
                owner_id="char_harry",
                type=InventoryType.CHARACTER,
                items=[item, item],
            )

    def test_capacity_exceeded_rejected(self):
        items = [InventoryItem(item_id=f"obj_item{i}", name=f"Item {i}") for i in range(3)]
        with pytest.raises(Exception):
            Inventory(
                inventory_id="inv_harry",
                owner_id="char_harry",
                type=InventoryType.CHARACTER,
                capacity=2,
                items=items,
            )


# ---------------------------------------------------------------------------
# Memory tests
# ---------------------------------------------------------------------------


class TestMemory:
    def test_valid_memory(self):
        mem = Memory(
            id="mem_001",
            character_id="char_hermione",
            timestamp=NOW,
            summary="Helped Harry with Potions homework.",
            type=MemoryType.CONVERSATION,
            importance=40,
        )
        assert mem.importance == 40

    def test_id_pattern_enforced(self):
        with pytest.raises(Exception):
            Memory(
                id="001",
                character_id="char_hermione",
                timestamp=NOW,
                summary="Test.",
            )

    def test_importance_range(self):
        with pytest.raises(Exception):
            Memory(
                id="mem_002",
                character_id="char_hermione",
                timestamp=NOW,
                summary="Test.",
                importance=101,
            )

    def test_requires_timestamp(self):
        """Memory without a timestamp must fail validation."""
        with pytest.raises(Exception):
            Memory(
                id="mem_003",
                character_id="char_hermione",
                summary="No timestamp.",
            )


# ---------------------------------------------------------------------------
# Emotion tests
# ---------------------------------------------------------------------------


class TestEmotion:
    def test_valid_emotion_state(self):
        es = EmotionState(
            character_id="char_harry",
            current_emotion=EmotionCategory.EXCITED,
            intensity=75,
            trigger="Quidditch match won",
            last_updated=NOW,
        )
        assert es.intensity == 75

    def test_intensity_range(self):
        with pytest.raises(Exception):
            EmotionState(character_id="char_harry", intensity=150)


# ---------------------------------------------------------------------------
# Scene tests
# ---------------------------------------------------------------------------


class TestScene:
    def test_valid_scene(self):
        scene = Scene(
            scene_id="scene_library",
            universe_id="hp_001",
            location=SceneLocationSummary(
                location_id="loc_library",
                name="Library",
            ),
            narration="Shelves of books stretch in every direction.",
            metadata=SceneMetadata(generation_timestamp=NOW),
        )
        assert scene.scene_id == "scene_library"

    def test_json_serialisable(self):
        scene = Scene(
            scene_id="scene_library",
            universe_id="hp_001",
            location=SceneLocationSummary(location_id="loc_library", name="Library"),
        )
        data = scene.model_dump_json()
        assert "scene_library" in data


# ---------------------------------------------------------------------------
# Snapshot tests
# ---------------------------------------------------------------------------


class TestSnapshot:
    def test_valid_snapshot(self):
        ws = WorldState(universe_id="hp_001")
        snap = Snapshot(
            snapshot_id="snap_001",
            universe_id="hp_001",
            world_state=ws,
            metadata=SnapshotMetadata(
                created_at=NOW,
                save_type=SnapshotSaveType.MANUAL,
                versions=SnapshotVersionMetadata(schema_version="1.0"),
            ),
        )
        assert snap.metadata.versions.schema_version == "1.0"

    def test_immutable(self):
        ws = WorldState(universe_id="hp_001")
        snap = Snapshot(
            snapshot_id="snap_001",
            universe_id="hp_001",
            world_state=ws,
            metadata=SnapshotMetadata(
                created_at=NOW,
                versions=SnapshotVersionMetadata(),
            ),
        )
        with pytest.raises(Exception):
            snap.snapshot_id = "snap_002"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Universe tests
# ---------------------------------------------------------------------------


class TestUniverse:
    def test_minimal_universe(self):
        uni = Universe(metadata=minimal_universe_metadata())
        assert uni.metadata.id == "hp_001"

    def test_duplicate_character_ids_rejected(self):
        char = minimal_character()
        with pytest.raises(Exception):
            Universe(metadata=minimal_universe_metadata(), characters=[char, char])

    def test_duplicate_location_ids_rejected(self):
        loc = minimal_location()
        with pytest.raises(Exception):
            Universe(metadata=minimal_universe_metadata(), locations=[loc, loc])

    def test_relationship_with_unknown_source_rejected(self):
        rel = Relationship(
            id="rel_ghost_harry",
            source="char_ghost",
            target="char_harry",
        )
        char = minimal_character()
        with pytest.raises(Exception):
            Universe(
                metadata=minimal_universe_metadata(),
                characters=[char],
                relationships=[rel],
            )

    def test_timeline_event_with_unknown_participant_rejected(self):
        event = TimelineEvent(
            id="evt_sorting",
            title="Sorting",
            sequence=1,
            participants=["char_unknown"],
        )
        with pytest.raises(Exception):
            Universe(
                metadata=minimal_universe_metadata(),
                timeline=Timeline(events=[event]),
            )

    def test_location_self_connection_rejected(self):
        loc = Location(
            id="loc_great_hall",
            name="Great Hall",
            connections=["loc_great_hall"],
        )
        with pytest.raises(Exception):
            Universe(metadata=minimal_universe_metadata(), locations=[loc])

    def test_get_character_returns_correct_instance(self):
        char = minimal_character()
        uni = Universe(metadata=minimal_universe_metadata(), characters=[char])
        assert uni.get_character("char_harry") is char

    def test_get_character_returns_none_for_missing_id(self):
        uni = Universe(metadata=minimal_universe_metadata())
        assert uni.get_character("char_nonexistent") is None

    def test_json_serialisable(self):
        uni = Universe(metadata=minimal_universe_metadata())
        data = uni.model_dump_json()
        assert "hp_001" in data

    def test_universe_is_frozen(self):
        uni = Universe(metadata=minimal_universe_metadata())
        with pytest.raises(Exception):
            uni.characters = []  # type: ignore[misc]

    def test_world_rule_id_pattern(self):
        with pytest.raises(Exception):
            WorldRule(
                id="magic",  # missing rule_ prefix
                name="Magic",
                category=WorldRuleCategory.MAGIC,
                description="Magic requires a wand.",
            )

    def test_valid_world_rule(self):
        rule = WorldRule(
            id="rule_magic_requires_wand",
            name="Magic Requires Wand",
            category=WorldRuleCategory.MAGIC,
            description="Only witches and wizards with a wand can cast spells.",
        )
        assert rule.immutable is True
