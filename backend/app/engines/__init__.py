"""
Headcanon Engines package.

Contains single-responsibility simulation, interaction, narrative presentation,
and media generation engines:
  - UniverseBuilder: Compiler transforming story text into validated Universe artifacts.
  - CharacterEngine: In-character reasoning and dialogue generation engine.
  - MemoryEngine: Character memory retrieval, decay, and candidate update evaluator.
  - RelationshipEngine: Multi-dimensional social metrics calculator and evaluator.
  - SceneEngine: Explorable UI scene constructor and narration generator.
  - InteractionEngine: Interaction controller parsing intent, validating, and routing user actions.
  - TimelineEngine: Chronological continuity recorder, event manager, and branch manager.
  - SimulationEngine: Core physics/consequence engine applying permanent WorldState mutations.
  - NarrationEngine: Narrative presentation engine converting scenes into rich prose.
  - MediaPipeline: Multimedia asset generator & provenance tracker.
"""

from app.engines.character_engine import CharacterEngine, CharacterEngineResponse
from app.engines.interaction_engine import InteractionEngine, InteractionResult, ParsedAction
from app.engines.media_pipeline import (
    AmbientAudioMetadata,
    AssetMetadata,
    MediaPipeline,
    MediaPipelineResult,
)
from app.engines.memory_engine import CandidateMemoryUpdate, MemoryEngine
from app.engines.narration_engine import NarrationEngine, NarrationResult
from app.engines.relationship_engine import ProposedRelationshipUpdate, RelationshipEngine
from app.engines.scene_engine import SceneEngine
from app.engines.simulation_engine import SimulationEngine, SimulationResult
from app.engines.timeline_engine import TimelineEngine
from app.engines.universe_builder import UniverseBuilder

__all__ = [
    "UniverseBuilder",
    "CharacterEngine",
    "CharacterEngineResponse",
    "MemoryEngine",
    "CandidateMemoryUpdate",
    "RelationshipEngine",
    "ProposedRelationshipUpdate",
    "SceneEngine",
    "InteractionEngine",
    "ParsedAction",
    "InteractionResult",
    "TimelineEngine",
    "SimulationEngine",
    "SimulationResult",
    "NarrationEngine",
    "NarrationResult",
    "MediaPipeline",
    "MediaPipelineResult",
    "AmbientAudioMetadata",
    "AssetMetadata",
]
