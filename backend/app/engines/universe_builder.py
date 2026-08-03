"""
Universe Builder — the compiler of Headcanon.

Transforms clean story text into a fully validated, immutable ``Universe``
object.  Every other engine in the runtime pipeline consumes this artifact.

Responsibilities (docs/engines/01_universe_builder.md §2):
  * Segment story text into manageable chunks
  * Extract characters, locations, objects, events, rules, and relationships
  * Merge duplicate entities across chunks
  * Build the knowledge graph from extracted entities
  * Initialise the starting World State
  * Validate cross-references and construct the final Universe

Non-responsibilities:
  * PDF / EPUB / web parsing (belongs to the import pipeline)
  * Gemini client construction (injected via dependency injection)
  * Storage (belongs to the storage layer)
  * Character dialogue, simulation, media generation

Pipeline stages (docs/engines/01_universe_builder.md §5):
  Story Text
    ↓ Stage 1 – Text Cleaning
    ↓ Stage 2 – Story Segmentation
    ↓ Stage 3 – Parallel Entity Extraction (per chunk)
    ↓ Stage 4 – Duplicate Merging
    ↓ Stage 5 – Knowledge Graph Construction
    ↓ Stage 6 – World Initialisation
    ↓ Stage 7 – Cross-reference Validation
    ↓ Stage 8 – Universe Assembly
  Universe
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from app.world.character import (
    Character,
    CharacterAbility,
    CharacterAppearance,
    CharacterGoal,
    CharacterKnowledge,
    CharacterMorality,
    CharacterPersonality,
    CharacterSpeech,
    EntityMetadata,
)
from app.world.knowledge_graph import (
    EdgeRelationship,
    GraphEdge,
    GraphNode,
    KnowledgeGraph,
    NodeType,
)
from app.world.location import Location, LocationCategory
from app.world.object import Object, ObjectCategory
from app.world.relationship import Relationship, RelationshipType
from app.world.timeline import EventStatus, EventType, Timeline, TimelineEvent, WorldTime
from app.world.universe import (
    ImportSource,
    Universe,
    UniverseMetadata,
    WorldRule,
    WorldRuleCategory,
)
from app.world.world_state import (
    CharacterState,
    LocationState,
    ObjectState,
    WorldState,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "universe"

# Maximum characters per story chunk fed to each extraction prompt.
# Context window safety margin: ~32 K chars ≈ ~8 K tokens at 4 chars/token.
_CHUNK_SIZE: int = 32_000

# Token by which to prefer splitting chunks (chapter / scene boundaries).
_CHUNK_SPLIT_PATTERNS: list[str] = [
    r"\bChapter\s+\d+",
    r"\bPart\s+\d+",
    r"\*\s*\*\s*\*",  # scene break: * * *
    r"---+",  # horizontal rule
    r"\n{3,}",  # three or more blank lines
]

_SCHEMA_VERSION = "1.0"


# ---------------------------------------------------------------------------
# Extraction result containers
# ---------------------------------------------------------------------------


@dataclass
class _ExtractionResult:
    """Aggregated raw-JSON outputs collected across all story chunks."""

    characters: list[dict[str, Any]] = field(default_factory=list)
    locations: list[dict[str, Any]] = field(default_factory=list)
    objects: list[dict[str, Any]] = field(default_factory=list)
    events: list[dict[str, Any]] = field(default_factory=list)
    rules: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public input / output dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class BuildRequest:
    """
    Input to the Universe Builder.

    Attributes:
        story_text:  Pre-cleaned story text (plain UTF-8).
        title:       Original story title.
        author:      Author name or ``"Unknown"``.
        source:      Import source format.
        language:    Primary language of the story.
        universe_id: Optional stable universe identifier.  Auto-generated if
                     omitted.
    """

    story_text: str
    title: str
    author: str = "Unknown"
    source: ImportSource = ImportSource.CUSTOM
    language: str = "English"
    universe_id: str | None = None


@dataclass(frozen=True)
class BuildResult:
    """
    Output from the Universe Builder.

    Attributes:
        universe: The fully validated, immutable Universe object.
        warnings: Non-fatal validation notices (e.g. missing optional fields).
    """

    universe: Universe
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Protocol — AI client interface
# ---------------------------------------------------------------------------


class AIClient:
    """
    Abstract interface for the language model backend.

    The Universe Builder is decoupled from the concrete Gemini client through
    this interface so that tests can inject a stub without making real API
    calls.

    Implementations must be thread-safe (the builder may call ``generate``
    concurrently in future iterations).
    """

    def generate(self, prompt: str) -> str:
        """
        Submit *prompt* to the model and return the raw text response.

        The response must be valid JSON as described in each prompt template.

        Raises:
            RuntimeError: If the model fails after all retries.
        """
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Universe Builder
# ---------------------------------------------------------------------------


class UniverseBuilder:
    """
    The compiler of Headcanon.

    Converts clean story text into a fully validated ``Universe`` object by
    orchestrating a series of focused extraction prompts and a multi-stage
    validation pipeline.

    All prompts are loaded from ``app/prompts/universe/`` at construction time
    so that IO errors surface immediately rather than mid-pipeline.

    Usage::

        client = GeminiClientAdapter(gemini_client)
        builder = UniverseBuilder(client)
        result = builder.build(
            BuildRequest(
                story_text=clean_text,
                title="Harry Potter and the Philosopher's Stone",
                author="J. K. Rowling",
            )
        )
        universe = result.universe

    Args:
        ai_client:   Injected AI client.  Must implement ``AIClient.generate``.
        prompt_dir:  Directory containing prompt ``.txt`` files.  Defaults to
                     the canonical ``app/prompts/universe/`` directory.
        chunk_size:  Maximum character count for a single extraction chunk.
                     Defaults to :data:`_CHUNK_SIZE`.
    """

    def __init__(
        self,
        ai_client: AIClient,
        prompt_dir: Path = _PROMPT_DIR,
        chunk_size: int = _CHUNK_SIZE,
    ) -> None:
        self._ai = ai_client
        self._prompt_dir = prompt_dir
        self._chunk_size = chunk_size
        self._prompts: dict[str, str] = self._load_all_prompts()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(self, request: BuildRequest) -> BuildResult:
        """
        Execute the full Universe reconstruction pipeline.

        Pipeline stages:
          1. Clean text
          2. Segment into chunks
          3. Extract entities from every chunk
          4. Merge duplicates across chunks
          5. Build the knowledge graph
          6. Initialise the World State
          7. Validate cross-references
          8. Assemble and return the Universe

        Args:
            request: :class:`BuildRequest` containing the clean story text and
                     metadata.

        Returns:
            :class:`BuildResult` with the validated :class:`Universe`.

        Raises:
            UniverseBuildError: If any mandatory pipeline stage fails or
                                produces an invalid Universe.
        """
        logger.info(
            "Universe Builder started: title=%r author=%r",
            request.title,
            request.author,
        )

        warnings: list[str] = []

        # Stage 1 — Text cleaning
        clean_text = self._clean_text(request.story_text)

        # Stage 2 — Segmentation
        chunks = self._segment(clean_text)
        logger.info("Story segmented into %d chunk(s)", len(chunks))

        # Stage 3 — Entity extraction (per chunk, sequential)
        result = _ExtractionResult()
        for index, chunk in enumerate(chunks):
            logger.info("Extracting entities from chunk %d/%d", index + 1, len(chunks))
            self._extract_chunk(chunk, result)

        logger.info(
            "Raw extraction totals: chars=%d locs=%d objs=%d evts=%d rules=%d rels=%d",
            len(result.characters),
            len(result.locations),
            len(result.objects),
            len(result.events),
            len(result.rules),
            len(result.relationships),
        )

        # Stage 4 — Duplicate merging
        result = self._merge_duplicates(result, warnings)

        # Stage 5 — Knowledge graph
        graph_data = self._build_graph(result)

        # Stage 6 — World initialisation
        world_state_data = self._initialise_world(result)

        # Stage 7 — Construct Pydantic models and validate
        universe = self._assemble_universe(
            request=request,
            result=result,
            graph_data=graph_data,
            world_state_data=world_state_data,
            warnings=warnings,
        )

        logger.info(
            "Universe Builder completed: id=%s chars=%d locs=%d objs=%d evts=%d",
            universe.metadata.id,
            len(universe.characters),
            len(universe.locations),
            len(universe.objects),
            len(universe.timeline.events),
        )

        return BuildResult(universe=universe, warnings=warnings)

    # ------------------------------------------------------------------
    # Stage 1 — Text Cleaning
    # ------------------------------------------------------------------

    def _clean_text(self, raw: str) -> str:
        """
        Remove artefacts that degrade extraction quality.

        Removes:
          * Page numbers (e.g. ``— 42 —``, ``Page 42``)
          * Repeated whitespace and trailing spaces
          * OCR artefacts (NUL bytes, control characters except newlines)
          * Broken paragraphs (single newline within a sentence mid-word)

        Preserves:
          * Dialogue
          * Chapter / scene headings
          * Paragraph breaks (double newlines)

        Args:
            raw: The original story text.

        Returns:
            Cleaned text suitable for chunking.
        """
        text = raw

        # Strip NUL bytes and control characters (except \n \r \t)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Normalise Windows line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove page numbers: standalone digits or decorated forms
        text = re.sub(r"(?m)^[ \t]*—?\s*\d+\s*—?[ \t]*$", "", text)
        text = re.sub(r"(?m)^\s*Page\s+\d+\s*$", "", text, flags=re.IGNORECASE)

        # Remove running headers / footers (lines ≤ 60 chars at block start/end)
        # Heuristic: remove lines appearing more than 5× that are very short.
        # (Too aggressive to implement reliably without OCR metadata; skip for now.)

        # Collapse runs of more than 3 blank lines to exactly 2
        text = re.sub(r"\n{4,}", "\n\n\n", text)

        # Remove trailing whitespace on each line
        text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

        # Collapse multiple spaces within a line (but not indentation)
        text = re.sub(r"(?<!\n) {2,}", " ", text)

        return text.strip()

    # ------------------------------------------------------------------
    # Stage 2 — Story Segmentation
    # ------------------------------------------------------------------

    def _segment(self, text: str) -> list[str]:
        """
        Split the story into chunks that fit within the model's context window.

        The splitter first tries to break at semantic boundaries (chapter
        headings, scene breaks) defined by :data:`_CHUNK_SPLIT_PATTERNS`.
        If no boundary is found within the chunk, it falls back to splitting
        at the nearest paragraph break, and ultimately at the character limit.

        Args:
            text: Cleaned story text.

        Returns:
            Ordered list of non-overlapping text chunks.  Each chunk is at
            most :attr:`_chunk_size` characters.
        """
        if len(text) <= self._chunk_size:
            return [text]

        # Build a combined regex for semantic split points
        split_re = re.compile(
            "|".join(f"(?:{p})" for p in _CHUNK_SPLIT_PATTERNS),
            flags=re.MULTILINE | re.IGNORECASE,
        )

        # Find all candidate split positions
        boundaries = [0] + [m.start() for m in split_re.finditer(text)] + [len(text)]

        chunks: list[str] = []
        current_start = 0

        for boundary in boundaries[1:]:
            segment_len = boundary - current_start
            if segment_len >= self._chunk_size:
                # Force-split at paragraph or space boundary within limit
                force_end = current_start + self._chunk_size
                para_break = text.rfind("\n\n", current_start, force_end)
                space_break = text.rfind(" ", current_start, force_end)
                split_at = (
                    para_break
                    if para_break > current_start
                    else (space_break if space_break > current_start else force_end)
                )
                chunk = text[current_start:split_at].strip()
                if chunk:
                    chunks.append(chunk)
                current_start = split_at
            elif boundary == len(text):
                # Last segment
                chunk = text[current_start:boundary].strip()
                if chunk:
                    chunks.append(chunk)
                current_start = boundary

        # Catch anything after the last forced split
        if current_start < len(text):
            tail = text[current_start:].strip()
            if tail:
                chunks.append(tail)

        return chunks if chunks else [text]

    # ------------------------------------------------------------------
    # Stage 3 — Entity extraction
    # ------------------------------------------------------------------

    def _extract_chunk(self, chunk: str, result: _ExtractionResult) -> None:
        """
        Run all six extraction prompts against a single story chunk and
        accumulate the raw JSON into *result*.

        Each extraction is attempted independently.  A failure in one
        extractor does NOT abort the others.  Errors are logged.

        Args:
            chunk:  A segment of the story text.
            result: Accumulator mutated in place.
        """
        extractors = [
            ("characters", "extract_characters.txt", "characters"),
            ("locations", "extract_locations.txt", "locations"),
            ("objects", "extract_objects.txt", "objects"),
            ("events", "extract_events.txt", "events"),
            ("rules", "extract_rules.txt", "rules"),
            ("relationships", "extract_relationships.txt", "relationships"),
        ]

        for field_name, prompt_file, json_key in extractors:
            try:
                raw = self._run_prompt(prompt_file, story=chunk)
                data = _parse_json(raw)
                items = data.get(json_key, [])
                if not isinstance(items, list):
                    logger.warning(
                        "Extractor '%s' returned non-list for key '%s'; skipping.",
                        prompt_file,
                        json_key,
                    )
                    continue
                getattr(result, field_name).extend(items)
            except Exception as exc:  # noqa: BLE001
                logger.error(
                    "Extraction failed for '%s': %s",
                    prompt_file,
                    exc,
                    exc_info=True,
                )

    # ------------------------------------------------------------------
    # Stage 4 — Duplicate Merging
    # ------------------------------------------------------------------

    def _merge_duplicates(
        self,
        result: _ExtractionResult,
        warnings: list[str],
    ) -> _ExtractionResult:
        """
        Deduplicate extracted entities by calling the merge_duplicates prompt,
        then fall back to a local ID-based deduplication strategy.

        The merge prompt is better at resolving aliases (e.g. "Harry" vs
        "Harry Potter").  The local deduplication catches any residual exact-ID
        duplicates.

        Args:
            result:   Raw aggregated extraction result.
            warnings: Mutable list to which non-fatal notices are appended.

        Returns:
            A new :class:`_ExtractionResult` with deduplicated entities.
        """
        merged = _ExtractionResult()

        for field_name in (
            "characters",
            "locations",
            "objects",
            "events",
            "rules",
            "relationships",
        ):
            raw_items: list[dict[str, Any]] = getattr(result, field_name)
            if not raw_items:
                continue

            try:
                prompt_input = json.dumps({field_name: raw_items}, ensure_ascii=False)
                raw = self._run_prompt("merge_duplicates.txt", universe=prompt_input)
                data = _parse_json(raw)
                entities = data.get("entities", raw_items)
                merged_items: list[dict[str, Any]] = (
                    entities if isinstance(entities, list) else raw_items
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Merge prompt failed for '%s': %s — falling back to local dedup.",
                    field_name,
                    exc,
                )
                merged_items = raw_items

            # Local deduplication: keep first occurrence of each ID
            seen_ids: set[str] = set()
            deduped: list[dict[str, Any]] = []
            for item in merged_items:
                item_id = str(item.get("id", ""))
                if not item_id:
                    # No ID — keep it (validators will catch it later)
                    deduped.append(item)
                    continue
                if item_id in seen_ids:
                    warnings.append(f"Duplicate {field_name} ID '{item_id}' removed during merge.")
                    continue
                seen_ids.add(item_id)
                deduped.append(item)

            getattr(merged, field_name).extend(deduped)

        logger.info(
            "Post-merge totals: chars=%d locs=%d objs=%d evts=%d rules=%d rels=%d",
            len(merged.characters),
            len(merged.locations),
            len(merged.objects),
            len(merged.events),
            len(merged.rules),
            len(merged.relationships),
        )
        return merged

    # ------------------------------------------------------------------
    # Stage 5 — Knowledge Graph Construction
    # ------------------------------------------------------------------

    def _build_graph(self, result: _ExtractionResult) -> dict[str, Any]:
        """
        Build the knowledge graph by calling the ``build_knowledge_graph``
        prompt with all extracted entities.

        Falls back to an empty graph on failure so that the rest of the
        pipeline can continue.

        Args:
            result: Merged extraction result.

        Returns:
            Raw graph data dictionary with ``"nodes"`` and ``"edges"`` keys.
        """
        entities_json = json.dumps(
            {
                "characters": result.characters,
                "locations": result.locations,
                "objects": result.objects,
                "events": result.events,
                "rules": result.rules,
                "relationships": result.relationships,
            },
            ensure_ascii=False,
        )
        try:
            raw = self._run_prompt("build_knowledge_graph.txt", universe=entities_json)
            data = _parse_json(raw)
            return {
                "nodes": data.get("nodes", []),
                "edges": data.get("edges", []),
            }
        except Exception as exc:  # noqa: BLE001
            logger.error("Knowledge graph build failed: %s", exc, exc_info=True)
            return {"nodes": [], "edges": []}

    # ------------------------------------------------------------------
    # Stage 6 — World Initialisation
    # ------------------------------------------------------------------

    def _initialise_world(self, result: _ExtractionResult) -> dict[str, Any]:
        """
        Call the ``initialize_world`` prompt to derive the starting World State
        from the extracted universe data.

        Falls back to an empty world state on failure so the pipeline can
        still produce a valid (though minimal) universe.

        Args:
            result: Merged extraction result.

        Returns:
            Raw world state data dictionary.
        """
        universe_json = json.dumps(
            {
                "characters": result.characters,
                "locations": result.locations,
                "objects": result.objects,
                "events": result.events,
            },
            ensure_ascii=False,
        )
        try:
            raw = self._run_prompt("initialize_world.txt", universe=universe_json)
            data = _parse_json(raw)
            return data.get("world_state", {})
        except Exception as exc:  # noqa: BLE001
            logger.error("World initialisation failed: %s", exc, exc_info=True)
            return {}

    # ------------------------------------------------------------------
    # Stage 7 / 8 — Assembly and Validation
    # ------------------------------------------------------------------

    def _assemble_universe(
        self,
        request: BuildRequest,
        result: _ExtractionResult,
        graph_data: dict[str, Any],
        world_state_data: dict[str, Any],
        warnings: list[str],
    ) -> Universe:
        """
        Convert raw extraction data into typed Pydantic models and perform
        final cross-reference validation by constructing the Universe object.

        Pydantic field and model validators on :class:`Universe` perform the
        authoritative validation.  This method additionally handles soft
        failures (invalid individual entities are logged and skipped rather
        than aborting the entire build).

        Args:
            request:          Original build request.
            result:           Merged extraction result.
            graph_data:       Raw knowledge graph dict.
            world_state_data: Raw world state dict.
            warnings:         Mutable warning list.

        Returns:
            Validated :class:`Universe`.

        Raises:
            UniverseBuildError: If the final Universe fails Pydantic validation.
        """
        now = datetime.now(tz=UTC)
        universe_id = request.universe_id or _generate_universe_id(request.title)

        metadata = UniverseMetadata(
            id=universe_id,
            title=request.title,
            author=request.author,
            source=request.source,
            language=request.language,
            created_at=now,
            schema_version=_SCHEMA_VERSION,
        )

        characters = self._build_characters(result.characters, warnings)
        locations = self._build_locations(result.locations, warnings)
        objects_ = self._build_objects(result.objects, warnings)
        timeline = self._build_timeline(result.events, warnings)
        rules = self._build_world_rules(result.rules, warnings)
        relationships = self._build_relationships(
            result.relationships,
            char_ids={c.id for c in characters},
            warnings=warnings,
        )
        knowledge_graph = self._build_knowledge_graph(graph_data, warnings)
        world_state = self._build_world_state(
            universe_id=universe_id,
            world_state_data=world_state_data,
            characters=characters,
            locations=locations,
            objects_=objects_,
            warnings=warnings,
        )

        try:
            universe = Universe(
                metadata=metadata,
                characters=characters,
                locations=locations,
                objects=objects_,
                relationships=relationships,
                timeline=timeline,
                world_rules=rules,
                knowledge_graph=knowledge_graph,
                world_state=world_state,
            )
        except (ValidationError, ValueError) as exc:
            raise UniverseBuildError(f"Universe validation failed after assembly: {exc}") from exc

        return universe

    # ------------------------------------------------------------------
    # Entity builders — Characters
    # ------------------------------------------------------------------

    def _build_characters(
        self,
        raw_chars: list[dict[str, Any]],
        warnings: list[str],
    ) -> list[Character]:
        """
        Convert raw character dicts from the extraction prompt into
        validated :class:`Character` models.

        Characters with an ID that does not start with ``char_`` are
        normalised automatically.  Characters that fail Pydantic validation
        are logged and skipped.

        Args:
            raw_chars: Raw character dicts from the extraction stage.
            warnings:  Mutable warning accumulator.

        Returns:
            List of valid :class:`Character` models.
        """
        characters: list[Character] = []
        for raw in raw_chars:
            char_id = _ensure_id_prefix(str(raw.get("id", "")), "char_")
            if not char_id or char_id == "char_":
                warnings.append(f"Character with blank ID skipped: {raw.get('name')!r}")
                continue

            personality = CharacterPersonality(
                traits=_as_list(raw.get("personality")),
            )
            speech = CharacterSpeech(
                tone=None,
                catchphrases=[],
                quirks=[],
            )

            # Goals — raw may be list of strings or list of dicts
            goals: list[CharacterGoal] = []
            for idx, g in enumerate(_as_list(raw.get("goals"))):
                if isinstance(g, str):
                    goals.append(CharacterGoal(id=f"goal_{char_id}_{idx}", title=g, priority=50))
                elif isinstance(g, dict):
                    goal_id = str(g.get("id", f"goal_{char_id}_{idx}"))
                    goals.append(
                        CharacterGoal(
                            id=goal_id,
                            title=str(g.get("title", g.get("description", "Unknown goal"))),
                            priority=int(g.get("priority", 50)),
                        )
                    )

            # Abilities — raw may be list of strings or list of dicts
            abilities: list[CharacterAbility] = []
            for idx, ab in enumerate(_as_list(raw.get("abilities"))):
                if isinstance(ab, str):
                    abilities.append(
                        CharacterAbility(
                            id=f"ability_{char_id}_{idx}",
                            name=ab,
                            description="",
                        )
                    )
                elif isinstance(ab, dict):
                    ab_id = str(ab.get("id", f"ability_{char_id}_{idx}"))
                    abilities.append(
                        CharacterAbility(
                            id=ab_id,
                            name=str(ab.get("name", ab_id)),
                            description=str(ab.get("description", "")),
                        )
                    )

            appearance = CharacterAppearance(
                clothing=str(raw.get("clothing", "") or ""),
            )

            knowledge = CharacterKnowledge(
                scope=_as_list(raw.get("knowledge")),
            )

            morality = CharacterMorality()

            try:
                char = Character(
                    id=char_id,
                    name=str(raw.get("name", char_id)),
                    aliases=_as_list(raw.get("aliases")),
                    species=raw.get("species") or None,
                    age=_safe_int(raw.get("age")),
                    occupation=raw.get("occupation") or None,
                    description=str(raw.get("appearance", raw.get("description", ""))),
                    appearance=appearance,
                    personality=personality,
                    speech=speech,
                    morality=morality,
                    goals=goals,
                    knowledge=knowledge,
                    abilities=abilities,
                    metadata=EntityMetadata(importance=50, confidence=0.9),
                )
                characters.append(char)
            except (ValidationError, ValueError) as exc:
                warnings.append(f"Character '{char_id}' skipped due to validation error: {exc}")
                logger.warning("Character '%s' skipped: %s", char_id, exc)

        return characters

    # ------------------------------------------------------------------
    # Entity builders — Locations
    # ------------------------------------------------------------------

    def _build_locations(
        self,
        raw_locs: list[dict[str, Any]],
        warnings: list[str],
    ) -> list[Location]:
        """
        Convert raw location dicts into validated :class:`Location` models.

        IDs are normalised to the ``loc_`` prefix.  Connections referencing
        the same location ID are stripped (self-loops).  Invalid locations
        are skipped with a warning.

        Args:
            raw_locs: Raw location dicts from the extraction stage.
            warnings: Mutable warning accumulator.

        Returns:
            List of valid :class:`Location` models.
        """
        locations: list[Location] = []
        for raw in raw_locs:
            loc_id = _ensure_id_prefix(str(raw.get("id", "")), "loc_")
            if not loc_id or loc_id == "loc_":
                warnings.append(f"Location with blank ID skipped: {raw.get('name')!r}")
                continue

            # Normalise connection IDs and strip self-loops
            raw_connections = [
                _ensure_id_prefix(str(c), "loc_")
                for c in _as_list(raw.get("connected_locations", raw.get("connections")))
                if str(c)
            ]
            connections = list(dict.fromkeys(c for c in raw_connections if c != loc_id))

            # Map raw type string to LocationCategory
            category = _map_location_category(str(raw.get("type", "")))

            try:
                loc = Location(
                    id=loc_id,
                    name=str(raw.get("name", loc_id)),
                    aliases=_as_list(raw.get("aliases")),
                    description=str(raw.get("description", "")),
                    category=category,
                    region=None,
                    parent_location=(
                        _ensure_id_prefix(str(raw["parent_location"]), "loc_")
                        if raw.get("parent_location")
                        else None
                    ),
                    connections=connections,
                    metadata=EntityMetadata(importance=50, confidence=0.9),
                )
                locations.append(loc)
            except (ValidationError, ValueError) as exc:
                warnings.append(f"Location '{loc_id}' skipped due to validation error: {exc}")
                logger.warning("Location '%s' skipped: %s", loc_id, exc)

        # Second pass: remove connections that reference unknown location IDs
        known_ids = {loc.id for loc in locations}
        cleaned: list[Location] = []
        for loc in locations:
            bad = [c for c in loc.connections if c not in known_ids]
            if bad:
                warnings.append(f"Location '{loc.id}': removed unknown connection(s) {bad}.")
                # Rebuild without bad connections
                loc = loc.model_copy(
                    update={"connections": [c for c in loc.connections if c in known_ids]}
                )
            cleaned.append(loc)

        return cleaned

    # ------------------------------------------------------------------
    # Entity builders — Objects
    # ------------------------------------------------------------------

    def _build_objects(
        self,
        raw_objs: list[dict[str, Any]],
        warnings: list[str],
    ) -> list[Object]:
        """
        Convert raw object dicts into validated :class:`Object` models.

        IDs are normalised to the ``obj_`` prefix.  Invalid objects are
        skipped with a warning.

        Args:
            raw_objs: Raw object dicts from the extraction stage.
            warnings: Mutable warning accumulator.

        Returns:
            List of valid :class:`Object` models.
        """
        objects_: list[Object] = []
        for raw in raw_objs:
            obj_id = _ensure_id_prefix(str(raw.get("id", "")), "obj_")
            if not obj_id or obj_id == "obj_":
                warnings.append(f"Object with blank ID skipped: {raw.get('name')!r}")
                continue

            category = _map_object_category(str(raw.get("type", raw.get("category", ""))))

            try:
                obj = Object(
                    id=obj_id,
                    name=str(raw.get("name", obj_id)),
                    aliases=_as_list(raw.get("aliases")),
                    category=category,
                    description=str(raw.get("description", "")),
                    abilities=_as_list(raw.get("abilities")),
                    metadata=EntityMetadata(importance=50, confidence=0.9),
                )
                objects_.append(obj)
            except (ValidationError, ValueError) as exc:
                warnings.append(f"Object '{obj_id}' skipped due to validation error: {exc}")
                logger.warning("Object '%s' skipped: %s", obj_id, exc)

        return objects_

    # ------------------------------------------------------------------
    # Entity builders — Timeline / Events
    # ------------------------------------------------------------------

    def _build_timeline(
        self,
        raw_events: list[dict[str, Any]],
        warnings: list[str],
    ) -> Timeline:
        """
        Convert raw event dicts into a validated :class:`Timeline`.

        Events are sorted by their order of appearance (list index) and
        assigned monotonically increasing sequence numbers.  Invalid events
        are skipped with a warning.

        Args:
            raw_events: Raw event dicts from the extraction stage.
            warnings:   Mutable warning accumulator.

        Returns:
            A :class:`Timeline` containing all valid events.
        """
        events: list[TimelineEvent] = []
        for seq, raw in enumerate(raw_events):
            evt_id = _ensure_id_prefix(str(raw.get("id", "")), "evt_")
            if not evt_id or evt_id == "evt_":
                evt_id = f"evt_event_{seq}"

            # Map raw participants (may be names or IDs)
            participants = [
                _ensure_id_prefix(str(p), "char_")
                for p in _as_list(raw.get("participants"))
                if str(p)
            ]

            location: str | None = None
            if raw.get("location"):
                location = _ensure_id_prefix(str(raw["location"]), "loc_")

            evt_type = _map_event_type(str(raw.get("type", "")))

            try:
                event = TimelineEvent(
                    id=evt_id,
                    title=str(raw.get("title", evt_id)),
                    description=str(raw.get("description", "")),
                    type=evt_type,
                    timestamp=None,
                    participants=list(dict.fromkeys(participants)),
                    location=location,
                    sequence=seq,
                    status=EventStatus.COMPLETED,
                    importance=_map_importance(str(raw.get("importance", "Normal"))),
                    metadata=EntityMetadata(importance=50, confidence=0.9),
                )
                events.append(event)
            except (ValidationError, ValueError) as exc:
                warnings.append(f"Event '{evt_id}' skipped due to validation error: {exc}")
                logger.warning("Event '%s' skipped: %s", evt_id, exc)

        return Timeline(
            current_time=WorldTime(day=1, hour=0),
            events=events,
            completed_events=[e.id for e in events if e.status == EventStatus.COMPLETED],
        )

    # ------------------------------------------------------------------
    # Entity builders — World Rules
    # ------------------------------------------------------------------

    def _build_world_rules(
        self,
        raw_rules: list[dict[str, Any]],
        warnings: list[str],
    ) -> list[WorldRule]:
        """
        Convert raw rule dicts into validated :class:`WorldRule` models.

        IDs are normalised to the ``rule_`` prefix.  Invalid rules are
        skipped with a warning.

        Args:
            raw_rules: Raw rule dicts from the extraction stage.
            warnings:  Mutable warning accumulator.

        Returns:
            List of valid :class:`WorldRule` models.
        """
        rules: list[WorldRule] = []
        for raw in raw_rules:
            rule_id = _ensure_id_prefix(str(raw.get("id", "")), "rule_")
            if not rule_id or rule_id == "rule_":
                warnings.append(f"Rule with blank ID skipped: {raw.get('title')!r}")
                continue

            category = _map_rule_category(str(raw.get("type", raw.get("category", ""))))

            description = str(raw.get("description", raw.get("title", "No description.")))
            if not description.strip():
                description = "No description provided."

            try:
                rule = WorldRule(
                    id=rule_id,
                    name=str(raw.get("title", raw.get("name", rule_id))),
                    category=category,
                    description=description,
                    priority=50,
                    exceptions=_as_list(raw.get("exceptions")),
                )
                rules.append(rule)
            except (ValidationError, ValueError) as exc:
                warnings.append(f"Rule '{rule_id}' skipped due to validation error: {exc}")
                logger.warning("Rule '%s' skipped: %s", rule_id, exc)

        return rules

    # ------------------------------------------------------------------
    # Entity builders — Relationships
    # ------------------------------------------------------------------

    def _build_relationships(
        self,
        raw_rels: list[dict[str, Any]],
        char_ids: set[str],
        warnings: list[str],
    ) -> list[Relationship]:
        """
        Convert raw relationship dicts into validated :class:`Relationship`
        models.

        Relationships referencing unknown character IDs are skipped rather
        than causing a hard failure.  Self-relationships are also rejected.

        Args:
            raw_rels:  Raw relationship dicts from the extraction stage.
            char_ids:  Set of valid character IDs for cross-reference checks.
            warnings:  Mutable warning accumulator.

        Returns:
            List of valid :class:`Relationship` models.
        """
        relationships: list[Relationship] = []
        for raw in raw_rels:
            # The prompt uses character_a / character_b; normalise to source / target
            source = _ensure_id_prefix(str(raw.get("source", raw.get("character_a", ""))), "char_")
            target = _ensure_id_prefix(str(raw.get("target", raw.get("character_b", ""))), "char_")

            if source == "char_" or target == "char_":
                warnings.append(f"Relationship with missing source/target skipped: {raw!r}")
                continue

            if source == target:
                warnings.append(f"Self-relationship for '{source}' skipped.")
                continue

            if source not in char_ids:
                warnings.append(
                    f"Relationship source '{source}' is not a known character — skipped."
                )
                continue

            if target not in char_ids:
                warnings.append(
                    f"Relationship target '{target}' is not a known character — skipped."
                )
                continue

            rel_id = _ensure_id_prefix(str(raw.get("id", "")), "rel_")
            if not rel_id or rel_id == "rel_":
                rel_id = f"rel_{source}_{target}"

            rel_type = _map_relationship_type(str(raw.get("type", "")))

            try:
                rel = Relationship(
                    id=rel_id,
                    source=source,
                    target=target,
                    type=rel_type,
                    metadata=EntityMetadata(importance=50, confidence=0.8),
                )
                relationships.append(rel)
            except (ValidationError, ValueError) as exc:
                warnings.append(f"Relationship '{rel_id}' skipped: {exc}")
                logger.warning("Relationship '%s' skipped: %s", rel_id, exc)

        return relationships

    # ------------------------------------------------------------------
    # Entity builders — Knowledge Graph
    # ------------------------------------------------------------------

    def _build_knowledge_graph(
        self,
        graph_data: dict[str, Any],
        warnings: list[str],
    ) -> KnowledgeGraph:
        """
        Convert raw graph data into a validated :class:`KnowledgeGraph`.

        Invalid nodes and edges are skipped with warnings rather than
        aborting the build.

        Args:
            graph_data: Raw dict with ``"nodes"`` and ``"edges"`` keys.
            warnings:   Mutable warning accumulator.

        Returns:
            Validated :class:`KnowledgeGraph`.
        """
        nodes: list[GraphNode] = []
        seen_node_ids: set[str] = set()

        for raw_node in graph_data.get("nodes", []):
            node_id = str(raw_node.get("id", ""))
            if not node_id:
                continue
            if node_id in seen_node_ids:
                warnings.append(f"Graph: duplicate node ID '{node_id}' skipped.")
                continue
            node_type = _map_node_type(str(raw_node.get("type", "")))
            try:
                node = GraphNode(
                    id=node_id,
                    type=node_type,
                    name=str(raw_node.get("label", raw_node.get("name", node_id))),
                )
                nodes.append(node)
                seen_node_ids.add(node_id)
            except (ValidationError, ValueError) as exc:
                warnings.append(f"Graph node '{node_id}' skipped: {exc}")

        edges: list[GraphEdge] = []
        seen_edges: set[tuple[str, str, str]] = set()

        for raw_edge in graph_data.get("edges", []):
            src = str(raw_edge.get("source", ""))
            tgt = str(raw_edge.get("target", ""))
            rel_raw = str(raw_edge.get("relation", raw_edge.get("relationship", "RELATED_TO")))
            rel = _map_edge_relationship(rel_raw)

            if not src or not tgt:
                continue
            if src == tgt:
                continue
            if src not in seen_node_ids or tgt not in seen_node_ids:
                continue  # silently drop dangling edges

            edge_key = (src, tgt, rel.value)
            if edge_key in seen_edges:
                continue  # no duplicate edges
            seen_edges.add(edge_key)

            try:
                edge = GraphEdge(source=src, target=tgt, relationship=rel)
                edges.append(edge)
            except (ValidationError, ValueError) as exc:
                warnings.append(f"Graph edge {src}→{tgt} skipped: {exc}")

        try:
            return KnowledgeGraph(nodes=nodes, edges=edges)
        except (ValidationError, ValueError) as exc:
            warnings.append(f"KnowledgeGraph validation failed, returning empty graph: {exc}")
            return KnowledgeGraph()

    # ------------------------------------------------------------------
    # Entity builders — World State
    # ------------------------------------------------------------------

    def _build_world_state(
        self,
        universe_id: str,
        world_state_data: dict[str, Any],
        characters: list[Character],
        locations: list[Location],
        objects_: list[Object],
        warnings: list[str],
    ) -> WorldState:
        """
        Construct the initial :class:`WorldState` from the world initialiser
        prompt output and the assembled canonical entities.

        Mutable character, location, and object states are populated from
        the AI output where available, and fall back to sensible defaults.

        Args:
            universe_id:      ID of the parent universe.
            world_state_data: Raw world state dict from the initialise_world prompt.
            characters:       Validated canonical characters.
            locations:        Validated canonical locations.
            objects_:         Validated canonical objects.
            warnings:         Mutable warning accumulator.

        Returns:
            Initial :class:`WorldState`.
        """
        char_states: dict[str, CharacterState] = {}
        for char in characters:
            char_states[char.id] = CharacterState(
                character_id=char.id,
                location=None,
                health="Healthy",
            )

        loc_states: dict[str, LocationState] = {}
        for loc in locations:
            loc_states[loc.id] = LocationState(
                location_id=loc.id,
                occupants=list(loc.occupants),
                objects=list(loc.objects),
            )

        obj_states: dict[str, ObjectState] = {}
        for obj in objects_:
            obj_states[obj.id] = ObjectState(
                object_id=obj.id,
                owner=obj.owner,
                location=obj.location,
            )

        # Overlay AI-derived character states where available
        for raw_cs in _as_list(world_state_data.get("character_states")):
            if not isinstance(raw_cs, dict):
                continue
            char_id = _ensure_id_prefix(
                str(raw_cs.get("id", raw_cs.get("character_id", ""))), "char_"
            )
            if char_id in char_states:
                loc_raw = raw_cs.get("current_location", raw_cs.get("location"))
                loc_id = _ensure_id_prefix(str(loc_raw), "loc_") if loc_raw else None
                char_states[char_id] = CharacterState(
                    character_id=char_id,
                    location=loc_id,
                    health=str(raw_cs.get("health", "Healthy")),
                    current_goal=raw_cs.get("current_goal") or None,
                    current_action=raw_cs.get("current_action") or None,
                )

        world_state = WorldState(
            universe_id=universe_id,
            time=WorldTime(day=1, hour=0),
            characters=char_states,
            locations=loc_states,
            objects=obj_states,
            flags={
                "world_initialized": True,
                "simulation_started": False,
                "user_joined": False,
            },
        )

        return world_state

    # ------------------------------------------------------------------
    # Prompt helpers
    # ------------------------------------------------------------------

    def _load_all_prompts(self) -> dict[str, str]:
        """
        Load every prompt template from :attr:`_prompt_dir` at startup.

        Returns:
            Mapping of filename → template text.

        Raises:
            UniverseBuildError: If the prompt directory does not exist or any
                                required prompt file is missing.
        """
        if not self._prompt_dir.is_dir():
            raise UniverseBuildError(f"Prompt directory not found: {self._prompt_dir}")

        required = [
            "extract_characters.txt",
            "extract_locations.txt",
            "extract_objects.txt",
            "extract_events.txt",
            "extract_rules.txt",
            "extract_relationships.txt",
            "build_knowledge_graph.txt",
            "initialize_world.txt",
            "merge_duplicates.txt",
        ]

        prompts: dict[str, str] = {}
        for filename in required:
            path = self._prompt_dir / filename
            if not path.exists():
                raise UniverseBuildError(f"Required prompt file not found: {path}")
            prompts[filename] = path.read_text(encoding="utf-8")
            logger.debug("Loaded prompt: %s (%d chars)", filename, len(prompts[filename]))

        return prompts

    def _run_prompt(self, filename: str, **kwargs: str) -> str:
        """
        Format the named prompt template with *kwargs* and submit it to the
        AI client.

        Args:
            filename: Prompt filename (e.g. ``"extract_characters.txt"``).
            **kwargs: Template variables.

        Returns:
            Raw AI response text.

        Raises:
            UniverseBuildError: If the prompt template is not loaded.
        """
        template = self._prompts.get(filename)
        if template is None:
            raise UniverseBuildError(f"Prompt '{filename}' was not pre-loaded.")

        prompt = template
        for key, value in kwargs.items():
            prompt = prompt.replace(f"{{{key}}}", value)

        logger.debug("Running prompt '%s'", filename)
        return self._ai.generate(prompt)


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------


class UniverseBuildError(RuntimeError):
    """
    Raised when the Universe Builder cannot produce a valid Universe.

    Wraps any underlying cause (validation errors, AI failures, missing
    prompts) as the ``__cause__``.
    """


# ---------------------------------------------------------------------------
# GeminiClient adapter
# ---------------------------------------------------------------------------


class GeminiClientAdapter(AIClient):
    """
    Adapts the existing :class:`~app.services.gemini_client.GeminiClient` to
    the :class:`AIClient` interface expected by :class:`UniverseBuilder`.

    This keeps the Universe Builder decoupled from the concrete Gemini
    implementation so tests can inject stubs.

    Args:
        gemini_client: An initialised ``GeminiClient`` instance.
    """

    def __init__(self, gemini_client: Any) -> None:
        self._client = gemini_client

    def generate(self, prompt: str) -> str:
        """Delegate to ``GeminiClient.generate_text``."""
        return self._client.generate_text(prompt)  # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# Private helpers — JSON parsing
# ---------------------------------------------------------------------------


def _parse_json(raw: str) -> dict[str, Any]:
    """
    Strip accidental markdown fences and parse JSON.

    The model occasionally wraps the JSON in triple backticks despite
    explicit instructions.  This function handles both fenced and bare JSON.

    Args:
        raw: Raw text response from the AI.

    Returns:
        Parsed JSON as a dictionary.

    Raises:
        ValueError: If the text cannot be parsed as JSON.
    """
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    try:
        result: dict[str, Any] = json.loads(text, strict=False)
        return result
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse AI JSON response: %s\nRaw (first 500):\n%s", exc, raw[:500])
        raise ValueError(f"AI returned invalid JSON: {exc}") from exc


# ---------------------------------------------------------------------------
# Private helpers — ID normalisation
# ---------------------------------------------------------------------------


def _ensure_id_prefix(raw_id: str, prefix: str) -> str:
    """
    Ensure *raw_id* starts with *prefix*.  If it already does, return as-is.
    If it is blank, return the prefix alone.

    Slugifies the raw ID by lowercasing and replacing spaces with underscores.

    Args:
        raw_id: Raw identifier from the AI extraction.
        prefix: Expected ID prefix (e.g. ``"char_"``).

    Returns:
        Normalised ID string.
    """
    slug = re.sub(r"\s+", "_", raw_id.strip().lower())
    slug = re.sub(r"[^a-z0-9_]", "", slug)
    if not slug:
        return prefix
    if slug.startswith(prefix):
        return slug
    return f"{prefix}{slug}"


def _generate_universe_id(title: str) -> str:
    """
    Generate a stable universe ID from the story title.

    Uses a short UUID4 suffix to guarantee uniqueness.

    Args:
        title: Story title.

    Returns:
        Universe ID string (e.g. ``"harry_potter_a1b2c3d4"``).
    """
    slug = re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")[:30]
    short_uuid = uuid.uuid4().hex[:8]
    return f"{slug}_{short_uuid}"


# ---------------------------------------------------------------------------
# Private helpers — type coercions
# ---------------------------------------------------------------------------


def _as_list(value: Any) -> list[Any]:
    """Return *value* as a list.  Scalars are wrapped; None returns ``[]``."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _safe_int(value: Any) -> int | None:
    """Attempt to cast *value* to int.  Returns ``None`` on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# ---------------------------------------------------------------------------
# Private helpers — enum mapping
# ---------------------------------------------------------------------------


def _map_location_category(raw: str) -> LocationCategory | None:
    """Map a raw location type string to :class:`LocationCategory`."""
    mapping: dict[str, LocationCategory] = {
        "castle": LocationCategory.CASTLE,
        "building": LocationCategory.BUILDING,
        "room": LocationCategory.ROOM,
        "forest": LocationCategory.FOREST,
        "village": LocationCategory.VILLAGE,
        "city": LocationCategory.CITY,
        "mountain": LocationCategory.MOUNTAIN,
        "dungeon": LocationCategory.DUNGEON,
        "spacecraft": LocationCategory.SPACECRAFT,
        "street": LocationCategory.STREET,
        "ocean": LocationCategory.OCEAN,
        "kingdom": LocationCategory.KINGDOM,
        "planet": LocationCategory.PLANET,
        "school": LocationCategory.BUILDING,
        "house": LocationCategory.BUILDING,
        "ship": LocationCategory.SPACECRAFT,
    }
    return mapping.get(raw.lower().strip())


def _map_object_category(raw: str) -> ObjectCategory | None:
    """Map a raw object type string to :class:`ObjectCategory`."""
    mapping: dict[str, ObjectCategory] = {
        "weapon": ObjectCategory.WEAPON,
        "book": ObjectCategory.BOOK,
        "potion": ObjectCategory.POTION,
        "tool": ObjectCategory.TOOL,
        "key": ObjectCategory.KEY,
        "vehicle": ObjectCategory.VEHICLE,
        "food": ObjectCategory.FOOD,
        "treasure": ObjectCategory.TREASURE,
        "artifact": ObjectCategory.ARTIFACT,
        "magic item": ObjectCategory.MAGIC_ITEM,
        "magical artifact": ObjectCategory.ARTIFACT,
        "clothing": ObjectCategory.CLOTHING,
        "document": ObjectCategory.DOCUMENT,
        "jewelry": ObjectCategory.TREASURE,
    }
    return mapping.get(raw.lower().strip())


def _map_event_type(raw: str) -> EventType:
    """Map a raw event type string to :class:`EventType`."""
    mapping: dict[str, EventType] = {
        "story": EventType.STORY_EVENT,
        "story event": EventType.STORY_EVENT,
        "character": EventType.STORY_EVENT,
        "combat": EventType.COMBAT,
        "travel": EventType.TRAVEL,
        "discovery": EventType.DISCOVERY,
        "conversation": EventType.STORY_EVENT,
        "magic": EventType.STORY_EVENT,
        "quest": EventType.STORY_EVENT,
        "political": EventType.STORY_EVENT,
        "relationship": EventType.STORY_EVENT,
        "object": EventType.STORY_EVENT,
        "user action": EventType.USER_ACTION,
        "world event": EventType.WORLD_EVENT,
        "simulation": EventType.SIMULATION,
    }
    return mapping.get(raw.lower().strip(), EventType.STORY_EVENT)


def _map_rule_category(raw: str) -> WorldRuleCategory:
    """Map a raw rule type string to :class:`WorldRuleCategory`."""
    mapping: dict[str, WorldRuleCategory] = {
        "magic": WorldRuleCategory.MAGIC,
        "physics": WorldRuleCategory.PHYSICS,
        "technology": WorldRuleCategory.TECHNOLOGY,
        "biology": WorldRuleCategory.BIOLOGY,
        "combat": WorldRuleCategory.COMBAT,
        "politics": WorldRuleCategory.POLITICS,
        "political": WorldRuleCategory.POLITICS,
        "religion": WorldRuleCategory.RELIGION,
        "society": WorldRuleCategory.SOCIAL,
        "social": WorldRuleCategory.SOCIAL,
        "organization": WorldRuleCategory.SOCIAL,
        "economy": WorldRuleCategory.ECONOMY,
        "geography": WorldRuleCategory.ENVIRONMENT,
        "environment": WorldRuleCategory.ENVIRONMENT,
        "object": WorldRuleCategory.INVENTORY,
        "lore": WorldRuleCategory.LORE,
        "movement": WorldRuleCategory.MOVEMENT,
    }
    return mapping.get(raw.lower().strip(), WorldRuleCategory.LORE)


def _map_relationship_type(raw: str) -> RelationshipType:
    """Map a raw relationship type string to :class:`RelationshipType`."""
    mapping: dict[str, RelationshipType] = {
        "friend": RelationshipType.FRIEND,
        "family": RelationshipType.FAMILY,
        "mentor": RelationshipType.MENTOR,
        "student": RelationshipType.STUDENT,
        "enemy": RelationshipType.ENEMY,
        "rival": RelationshipType.RIVAL,
        "romantic": RelationshipType.ROMANTIC,
        "ally": RelationshipType.ALLY,
        "employer": RelationshipType.EMPLOYER,
        "employee": RelationshipType.FOLLOWER,
        "leader": RelationshipType.EMPLOYER,
        "follower": RelationshipType.FOLLOWER,
        "companion": RelationshipType.COMPANION,
    }
    return mapping.get(raw.lower().strip(), RelationshipType.NEUTRAL)


def _map_importance(raw: str) -> int:
    """Convert a qualitative importance label to a numeric score (0–100)."""
    mapping = {
        "critical": 90,
        "major": 70,
        "normal": 50,
        "minor": 30,
        "background": 10,
        "legendary": 95,
        "quest": 80,
        "unknown": 50,
    }
    return mapping.get(raw.lower().strip(), 50)


def _map_node_type(raw: str) -> NodeType:
    """Map a raw node type string to :class:`NodeType`."""
    mapping: dict[str, NodeType] = {
        "character": NodeType.CHARACTER,
        "location": NodeType.LOCATION,
        "object": NodeType.OBJECT,
        "event": NodeType.EVENT,
        "rule": NodeType.RULE,
        "faction": NodeType.FACTION,
        "species": NodeType.SPECIES,
        "organization": NodeType.ORGANIZATION,
        "creature": NodeType.CHARACTER,
    }
    return mapping.get(raw.lower().strip(), NodeType.CHARACTER)


def _map_edge_relationship(raw: str) -> EdgeRelationship:
    """Map a raw edge relation string to :class:`EdgeRelationship`."""
    mapping: dict[str, EdgeRelationship] = {
        "knows": EdgeRelationship.KNOWS,
        "friend_of": EdgeRelationship.FRIEND_OF,
        "enemy_of": EdgeRelationship.ENEMY_OF,
        "mentors": EdgeRelationship.KNOWS,
        "member_of": EdgeRelationship.MEMBER_OF,
        "lives_in": EdgeRelationship.LIVES_IN,
        "located_in": EdgeRelationship.LOCATED_IN,
        "owns": EdgeRelationship.OWNS,
        "uses": EdgeRelationship.USES,
        "created": EdgeRelationship.OWNS,
        "destroyed": EdgeRelationship.OWNS,
        "visited": EdgeRelationship.VISITED,
        "participated_in": EdgeRelationship.PARTICIPATED_IN,
        "triggered": EdgeRelationship.CAUSED,
        "depends_on": EdgeRelationship.REQUIRES,
        "affects": EdgeRelationship.AFFECTED,
        "contains": EdgeRelationship.LOCATED_IN,
        "connected_to": EdgeRelationship.LIVES_IN,
        "related_to": EdgeRelationship.AFFECTED,
        "friend of": EdgeRelationship.FRIEND_OF,
        "enemy of": EdgeRelationship.ENEMY_OF,
        "lives in": EdgeRelationship.LIVES_IN,
        "located in": EdgeRelationship.LOCATED_IN,
        "participated in": EdgeRelationship.PARTICIPATED_IN,
    }
    return mapping.get(raw.lower().strip(), EdgeRelationship.AFFECTED)
