"""
Relationship Engine for Headcanon.

Evaluates, calculates, clamps, and formats social relationship metrics and updates
between characters.

Reference: docs/engines/07_relationship_engine.md
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.world.relationship import Relationship, RelationshipScores, RelationshipType

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "characters"


class ProposedRelationshipUpdate(BaseModel, frozen=True):
    """
    Proposed relationship metric changes for a character pair.

    Does NOT persist changes directly.
    """

    source_character: str = Field(min_length=1)
    target_character: str = Field(min_length=1)
    changes: dict[str, int] = Field(default_factory=dict)
    reason: str = ""


class RelationshipEngine:
    """
    Social relationship calculator and evaluator for Headcanon characters.

    Responsibilities:
      - Evaluate relationship deltas via relationship_update LLM prompt
      - Enforce metric bounds [-100, 100] and delta limits (max +/-10 per interaction)
      - Infer high-level RelationshipType from metric scores
      - Build formatted relationship context strings for Character Engine context window

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
            prompt_file = self.prompt_dir / "relationship_update.txt"
            if not prompt_file.exists():
                raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
            self._prompt_template = prompt_file.read_text(encoding="utf-8")
        return self._prompt_template

    def clamp_score(self, value: int, min_val: int = 0, max_val: int = 100) -> int:
        """Clamp numeric score within [0, 100] bounds."""
        return max(min_val, min(max_val, value))

    def calculate_delta(
        self,
        current_scores: RelationshipScores,
        changes: dict[str, int],
        max_delta: int = 10,
    ) -> RelationshipScores:
        """
        Calculate updated relationship scores while enforcing max single-interaction deltas
        and [0, 100] metric bounds.

        Args:
            current_scores: Existing RelationshipScores instance.
            changes: Dict of metric deltas (e.g. {"trust": 4, "affection": 2}).
            max_delta: Maximum allowed change in a single interaction (+/-10).

        Returns:
            Updated RelationshipScores model.
        """
        updated_dict = current_scores.model_dump()

        # Handle 'affinity' alias -> 'affection' if present in LLM output
        if "affinity" in changes and "affection" not in changes:
            changes["affection"] = changes["affinity"]

        for key, delta in changes.items():
            if key in updated_dict:
                # Limit single delta
                bounded_delta = max(-max_delta, min(max_delta, int(delta)))
                new_val = self.clamp_score(updated_dict[key] + bounded_delta)
                updated_dict[key] = new_val

        return RelationshipScores(**updated_dict)

    def infer_relationship_type(self, scores: RelationshipScores) -> RelationshipType:
        """
        Infer a high-level RelationshipType enum from relationship metrics.

        Args:
            scores: RelationshipScores model instance.

        Returns:
            Inferred RelationshipType enum.
        """
        if scores.affection <= 20 or scores.trust <= 20:
            return RelationshipType.ENEMY
        if scores.affection >= 70 and scores.trust >= 70:
            return RelationshipType.FRIEND
        if scores.respect >= 70 and scores.trust >= 50:
            return RelationshipType.MENTOR
        if scores.affection >= 50 and scores.trust >= 50:
            return RelationshipType.ALLY
        return RelationshipType.NEUTRAL

    def evaluate_relationship_updates(
        self,
        source_character: str,
        target_character: str,
        current_relationship: Relationship | None,
        user_action: str,
        interaction_summary: str,
        emotion: str | None = None,
    ) -> list[ProposedRelationshipUpdate]:
        """
        Call LLM relationship_update prompt to evaluate social relationship changes.

        Args:
            source_character: Source character ID.
            target_character: Target character ID.
            current_relationship: Existing Relationship model or None.
            user_action: User action text.
            interaction_summary: Summary of recent interaction.
            emotion: Character's current emotion.

        Returns:
            List of ProposedRelationshipUpdate models.
        """
        if self.ai_client is None:
            logger.warning("No AIClient provided to RelationshipEngine; skipping LLM evaluation.")
            return []

        template = self._get_prompt_template()
        scores_dict = (
            current_relationship.scores.model_dump()
            if current_relationship
            else RelationshipScores().model_dump()
        )

        replacements = {
            "character_profile": source_character,
            "current_relationship_graph": json.dumps(
                {target_character: scores_dict}, ensure_ascii=False
            ),
            "character_memories": "N/A",
            "latest_interaction": f"Action: {user_action}\nSummary: {interaction_summary}",
            "current_emotional_state": emotion or "Calm",
            "timeline_position": "Active",
        }

        prompt = template
        for k, v in replacements.items():
            prompt = prompt.replace(f"{{{k}}}", str(v))

        try:
            raw_response = self.ai_client.generate(prompt)
            parsed = _parse_json(raw_response)
            raw_updates = parsed.get("relationship_updates", [])

            updates: list[ProposedRelationshipUpdate] = []
            for item in raw_updates:
                src = item.get("source_character", source_character)
                tgt = item.get("target_character", target_character)
                changes = item.get("changes", {})
                reason = item.get("reason", "")
                if src and tgt and isinstance(changes, dict):
                    updates.append(
                        ProposedRelationshipUpdate(
                            source_character=src,
                            target_character=tgt,
                            changes=changes,
                            reason=reason,
                        )
                    )

            return updates
        except Exception as exc:
            logger.warning("Relationship evaluation LLM call failed: %s", exc)
            return []

    def build_relationship_context(
        self,
        relationships: list[Relationship],
        character_id: str | None = None,
    ) -> str:
        """
        Format relationship context string for inclusion in prompt templates.

        Args:
            relationships: List of Relationship models.
            character_id: Optional filter for a specific character.

        Returns:
            Formatted relationship string.
        """
        if not relationships:
            return "No established relationships."

        lines: list[str] = []
        for rel in relationships:
            if character_id and rel.source != character_id and rel.target != character_id:
                continue
            lines.append(
                f"- {rel.source} -> {rel.target} ({rel.type.value}): "
                f"Trust={rel.scores.trust}, Affection={rel.scores.affection}, "
                f"Respect={rel.scores.respect}"
            )

        return "\n".join(lines) if lines else "No relevant relationships."


def _parse_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1]).strip()
    return json.loads(text, strict=False)
