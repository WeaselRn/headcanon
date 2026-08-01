"""
Knowledge Graph data models for Headcanon.

The Knowledge Graph is the semantic backbone of the universe.  Every entity
becomes a **node**; every relationship between entities becomes a **directed
edge**.  This enables the Character Engine and Simulation Engine to reason
about the world without scanning every collection.

Reference: docs/universe/8_knowledge_graph.md, docs/universe/1_universe_schema §12
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator, model_validator

from app.world.character import EntityMetadata

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class NodeType(StrEnum):
    """Entity type represented by a graph node."""

    CHARACTER = "Character"
    LOCATION = "Location"
    OBJECT = "Object"
    EVENT = "Event"
    RULE = "Rule"
    FACTION = "Faction"
    SPECIES = "Species"
    ORGANIZATION = "Organization"
    QUEST = "Quest"
    USER = "User"


class EdgeRelationship(StrEnum):
    """Directed relationship label for a graph edge."""

    LIVES_IN = "Lives In"
    OWNS = "Owns"
    KNOWS = "Knows"
    VISITED = "Visited"
    USES = "Uses"
    CREATED = "Created"
    DESTROYED = "Destroyed"
    FRIEND_OF = "Friend Of"
    ENEMY_OF = "Enemy Of"
    MEMBER_OF = "Member Of"
    LOCATED_IN = "Located In"
    OCCURRED_AT = "Occurred At"
    REQUIRES = "Requires"
    CAUSED = "Caused"
    AFFECTED = "Affected"
    PROTECTS = "Protects"
    PARTICIPATED_IN = "Participated In"


# ---------------------------------------------------------------------------
# Sub-models
# ---------------------------------------------------------------------------


class GraphNode(BaseModel, frozen=True):
    """
    A node in the Knowledge Graph representing a single universe entity.

    Attributes:
        id:         Entity ID (must match the ID used in the entity's own model).
        type:       Entity type category.
        name:       Human-readable display label.
        properties: Optional additional attributes for reasoning.
    """

    id: str = Field(min_length=1)
    type: NodeType
    name: str = Field(min_length=1)
    properties: dict[str, str | int | float | bool] = Field(default_factory=dict)


class GraphEdge(BaseModel, frozen=True):
    """
    A directed edge in the Knowledge Graph.

    Edges are **always directed**:  ``source → target``.

    Attributes:
        source:       Source entity ID.
        target:       Target entity ID.
        relationship: The type of connection.
        weight:       Optional weight (e.g. trust score, visit count).
        properties:   Optional additional attributes.
    """

    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    relationship: EdgeRelationship
    weight: float = Field(default=1.0, ge=0.0)
    properties: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("source", "target")
    @classmethod
    def ids_non_empty(cls, v: str) -> str:
        """Node IDs must not be empty or whitespace."""
        if not v.strip():
            raise ValueError("Graph edge node ID must not be empty.")
        return v

    @model_validator(mode="after")
    def source_differs_from_target(self) -> GraphEdge:
        """A self-loop edge is not permitted."""
        if self.source == self.target:
            raise ValueError(f"Graph edge source and target must differ (got '{self.source}').")
        return self


# ---------------------------------------------------------------------------
# Root model
# ---------------------------------------------------------------------------


class KnowledgeGraph(BaseModel):
    """
    The complete entity graph for a universe.

    Nodes represent entities; edges represent directed relationships between
    them.  The graph is built by the Universe Builder and updated by the
    Simulation Engine after every significant event.

    Attributes:
        nodes:    All entity nodes.
        edges:    All directed relationship edges.
        metadata: Shared entity metadata.
    """

    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    metadata: EntityMetadata = Field(default_factory=EntityMetadata)

    @model_validator(mode="after")
    def node_ids_are_unique(self) -> KnowledgeGraph:
        """Node IDs must be unique within the graph."""
        ids = [n.id for n in self.nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("Knowledge Graph node IDs must be unique.")
        return self

    @model_validator(mode="after")
    def edge_references_exist(self) -> KnowledgeGraph:
        """
        Every edge must reference node IDs that exist within the graph.

        Raises:
            ValueError: If any dangling edge reference is detected.
        """
        node_id_set = {n.id for n in self.nodes}
        dangling: list[str] = []
        for edge in self.edges:
            if edge.source not in node_id_set:
                dangling.append(f"edge source '{edge.source}'")
            if edge.target not in node_id_set:
                dangling.append(f"edge target '{edge.target}'")
        if dangling:
            raise ValueError(f"Knowledge Graph contains dangling edge references: {dangling}")
        return self
