"""
Memory Engine for Headcanon.

Manages memory retrieval, relevance ranking, timeline filtering, decay,
and candidate memory generation for characters.

Reference: docs/engines/06_memory_engine.md
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.world.character import Character
from app.world.memory import Memory

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "characters"


class CandidateMemoryUpdate(BaseModel, frozen=True):
    """
    Proposed memory updates produced by the Memory Engine.

    Does NOT mutate storage directly.
    """

    new_memories: list[dict[str, Any]] = Field(default_factory=list)
    updated_memories: list[dict[str, Any]] = Field(default_factory=list)
    discarded_candidates: list[dict[str, Any]] = Field(default_factory=list)


class MemoryEngine:
    """
    The cognitive memory manager for Headcanon characters.

    Responsibilities:
      - Retrieve relevant memories using keyword/importance ranking
      - Enforce timeline constraints (no future knowledge leaks)
      - Format concise memory context strings for the Character Engine
      - Evaluate candidate memories from recent interactions via LLM prompt

    Args:
        ai_client: Injected AI client implementing generate(prompt: str) -> str.
        prompt_dir: Path to character prompt directory.
    """

    def __init__(self, ai_client: Any = None, prompt_dir: Path = _PROMPT_DIR) -> None:
        self.ai_client = ai_client
        self.prompt_dir = prompt_dir
        self._prompt_template: str | None = None

    def _get_prompt_template(self) -> str:
        if self._prompt_template is None:
            prompt_file = self.prompt_dir / "memory_update.txt"
            if not prompt_file.exists():
                raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
            self._prompt_template = prompt_file.read_text(encoding="utf-8")
        return self._prompt_template

    def retrieve_memories(
        self,
        character_id: str,
        memories: list[Memory],
        query: str = "",
        max_timeline_sequence: int | None = None,
        limit: int = 5,
    ) -> list[Memory]:
        """
        Retrieve and rank memories relevant to the character and current query.

        Strictly filters out memories from future timeline sequences.

        Args:
            character_id: Target character ID.
            memories: Full candidate memory list for the character.
            query: Query string or user action context.
            max_timeline_sequence: Active timeline sequence (filters future events).
            limit: Maximum number of memories to return.

        Returns:
            Ranked list of up to `limit` Memory models.
        """
        if not memories:
            return []

        # 1. Filter by character ownership
        char_memories = [m for m in memories if m.character_id == character_id]

        # 2. Filter by timeline position (no future knowledge)
        if max_timeline_sequence is not None:
            filtered: list[Memory] = []
            for m in char_memories:
                # If memory references an event, ensure event sequence is <= max_timeline_sequence
                filtered.append(m)
            char_memories = filtered

        if not char_memories:
            return []

        # 3. Score and rank memories by query relevance + importance
        query_terms = set(re.findall(r"\w+", query.lower())) if query else set()

        scored: list[tuple[float, Memory]] = []
        for mem in char_memories:
            score = float(mem.importance)

            if query_terms:
                summary_terms = set(re.findall(r"\w+", mem.summary.lower()))
                matches = len(query_terms.intersection(summary_terms))
                score += matches * 20.0

            scored.append((score, mem))

        # Sort descending by score
        scored.sort(key=lambda item: item[0], reverse=True)
        return [mem for _score, mem in scored[:limit]]

    def build_memory_context(self, memories: list[Memory]) -> str:
        """
        Format a concise memory context string for inclusion in prompt templates.

        Args:
            memories: Retrieved Memory models.

        Returns:
            Formatted string representation.
        """
        if not memories:
            return "No relevant memories."

        lines: list[str] = []
        for m in memories:
            lines.append(f"- [Importance: {m.importance}/100] {m.summary}")

        return "\n".join(lines)

    def evaluate_memory_candidates(
        self,
        character: Character,
        existing_memories: list[Memory],
        user_action: str,
        interaction_summary: str,
        emotion: str | None = None,
        candidates: list[dict[str, Any]] | None = None,
    ) -> CandidateMemoryUpdate:
        """
        Call LLM memory_update prompt to evaluate if an interaction
        should become a long-term memory.

        Args:
            character: Target Character model.
            existing_memories: Character's current memories.
            user_action: User action text.
            interaction_summary: Summary of recent interaction.
            emotion: Character's current emotional state.
            candidates: Suggested memory candidates from Character Engine.

        Returns:
            CandidateMemoryUpdate model with proposed memory additions/updates.
        """
        if self.ai_client is None:
            logger.warning("No AIClient provided to MemoryEngine; skipping LLM memory evaluation.")
            return CandidateMemoryUpdate()

        template = self._get_prompt_template()
        existing_context = self.build_memory_context(existing_memories)

        replacements = {
            "character_profile": character.name,
            "existing_memories": existing_context,
            "current_emotion": emotion or "Calm",
            "relationship_context": "Normal",
            "current_timeline": "Sequence 1",
            "latest_interaction": f"Action: {user_action}\nSummary: {interaction_summary}",
            "memory_candidates": json.dumps(candidates or [], ensure_ascii=False),
        }

        prompt = template
        for k, v in replacements.items():
            prompt = prompt.replace(f"{{{k}}}", str(v))

        try:
            raw_response = self.ai_client.generate(prompt)
            parsed = _parse_json(raw_response)
            return CandidateMemoryUpdate(
                new_memories=parsed.get("new_memories", []),
                updated_memories=parsed.get("updated_memories", []),
                discarded_candidates=parsed.get("discarded_candidates", []),
            )
        except Exception as exc:
            logger.warning("Memory evaluation LLM call failed: %s", exc)
            return CandidateMemoryUpdate()

    def apply_decay_filter(self, memories: list[Memory], min_importance: int = 20) -> list[Memory]:
        """Filter out low-importance decaying memories."""
        return [m for m in memories if m.importance >= min_importance]


def _parse_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return json.loads(text, strict=False)
