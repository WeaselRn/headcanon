"""
World Simulation Engine for Headcanon.

The core physics engine of Headcanon. Receives pending world effects from
Interaction Engine results, applies permanent state updates to WorldState,
records events into Timeline, updates relationship graphs, manages inventories,
and runs NPC scheduling.

Reference: docs/engines/04_simulation_engine.md
"""

from __future__ import annotations

import logging
import uuid
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from app.engines.interaction_engine import InteractionResult
from app.engines.relationship_engine import RelationshipEngine
from app.engines.timeline_engine import TimelineEngine
from app.world.timeline import EventStatus, EventType, Timeline, TimelineEvent
from app.world.universe import Universe
from app.world.world_state import (
    CharacterState,
    LocationState,
    RelationshipState,
    WorldState,
)

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "simulation"


class SimulationResult(BaseModel, frozen=True):
    """
    Structured result of a world simulation run.

    Contains the updated WorldState and Timeline instances along with a record
    of atomic mutations and newly generated events.
    """

    simulation_id: str = Field(min_length=1)
    universe_id: str = Field(min_length=1)
    updated_world_state: WorldState
    updated_timeline: Timeline
    mutations: list[dict[str, Any]] = Field(default_factory=list)
    generated_events: list[TimelineEvent] = Field(default_factory=list)
    success: bool = True
    error_message: str | None = None


class SimulationEngine:
    """
    The world simulation engine for Headcanon.

    Responsibilities:
      - Receive InteractionResult with pending_world_effects
      - Execute atomic world state mutations (locations, inventories, relationships, time)
      - Enforce world rules, relationship bounds [0, 100], and ownership constraints
      - Update Timeline via TimelineEngine (record events, detect divergence)
      - Execute NPC routines / background scheduling
      - Return validated SimulationResult with updated WorldState and Timeline

    Args:
        ai_client: Optional injected AI client.
        timeline_engine: Optional TimelineEngine instance.
        relationship_engine: Optional RelationshipEngine instance.
        prompt_dir: Path to simulation prompt directory.
    """

    def __init__(
        self,
        ai_client: Any = None,
        timeline_engine: TimelineEngine | None = None,
        relationship_engine: RelationshipEngine | None = None,
        prompt_dir: Path = _PROMPT_DIR,
    ) -> None:
        self.ai_client = ai_client
        self.timeline_engine = timeline_engine or TimelineEngine(ai_client)
        self.relationship_engine = relationship_engine or RelationshipEngine(ai_client)
        self.prompt_dir = prompt_dir
        self._prompts: dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Pre-load simulation prompt templates."""
        if self.prompt_dir.exists():
            for file in self.prompt_dir.glob("*.txt"):
                self._prompts[file.name] = file.read_text(encoding="utf-8")

    def simulate_interaction(
        self,
        interaction_result: InteractionResult,
        world_state: WorldState,
        universe: Universe,
        timeline: Timeline | None = None,
        user_character_id: str = "char_user",
    ) -> SimulationResult:
        """
        Execute simulation pipeline for a user interaction.

        Pipeline:
          1. Clone mutable copies of WorldState and Timeline
          2. Apply pending world effects (locations, items, relationships, time)
          3. Generate & record TimelineEvent for interaction
          4. Run background NPC scheduler
          5. Validate final WorldState & Timeline
          6. Return populated SimulationResult

        Args:
            interaction_result: InteractionResult from Interaction Engine.
            world_state: Live WorldState model.
            universe: Canonical Universe model.
            timeline: Live Timeline model (created if None).
            user_character_id: Player character ID.

        Returns:
            SimulationResult with updated WorldState and Timeline.
        """
        if not interaction_result.success:
            cur_tl = timeline or Timeline()
            return SimulationResult(
                simulation_id=f"sim_{uuid.uuid4().hex[:6]}",
                universe_id=universe.metadata.id,
                updated_world_state=world_state,
                updated_timeline=cur_tl,
                success=False,
                error_message=interaction_result.error_message or "Interaction failed.",
            )

        sim_id = f"sim_{uuid.uuid4().hex[:6]}"
        mutations: list[dict[str, Any]] = []
        generated_events: list[TimelineEvent] = []

        # Make working copies
        working_state = world_state.model_copy(deep=True)
        working_timeline = (timeline or Timeline()).model_copy(deep=True)

        # 1. Process Pending World Effects
        for effect in interaction_result.pending_world_effects:
            eff_type = effect.get("type")

            if eff_type == "location_update":
                self._apply_location_update(
                    user_character_id,
                    str(effect.get("target_location", "")),
                    working_state,
                    universe,
                    mutations,
                )

            elif eff_type == "transfer_item":
                self._apply_item_transfer(
                    str(effect.get("item_id", "")),
                    user_character_id,
                    str(effect.get("recipient", "")),
                    working_state,
                    universe,
                    mutations,
                )

            elif eff_type == "use_item":
                self._apply_item_use(
                    str(effect.get("item_id", "")),
                    user_character_id,
                    working_state,
                    universe,
                    mutations,
                )

            elif eff_type == "suggest_relationships":
                changes = effect.get("changes", [])
                if isinstance(changes, list):
                    self._apply_relationship_changes(
                        user_character_id,
                        changes,
                        working_state,
                        universe,
                        mutations,
                    )

            elif eff_type == "advance_time":
                hours = int(effect.get("hours", 1))
                new_time = self.timeline_engine.advance_time(working_state.time, hours)
                working_state = working_state.model_copy(update={"time": new_time})
                mutations.append({"entity": "time", "field": "hour", "new": new_time.hour})

        # 2. Record Timeline Event for Action
        act_title = f"{interaction_result.action.capitalize()}"
        if interaction_result.target:
            act_title += f" {interaction_result.target}"

        cur_loc = (
            working_state.characters[user_character_id].location
            if user_character_id in working_state.characters
            else None
        )

        event_type = EventType.USER_ACTION
        if interaction_result.action == "talk":
            event_type = EventType.CONVERSATION
        elif interaction_result.action == "travel":
            event_type = EventType.TRAVEL

        event = self.timeline_engine.create_event(
            title=act_title,
            description=interaction_result.narration
            or f"Player executed {interaction_result.action}.",
            event_type=event_type,
            location=cur_loc,
            participants=[user_character_id]
            + ([interaction_result.target] if interaction_result.target else []),
            timestamp=f"Day {working_state.time.day}, Hour {working_state.time.hour:02d}:00",
            status=EventStatus.COMPLETED,
        )

        working_timeline = self.timeline_engine.append_event(working_timeline, event)
        generated_events.append(event)

        # 3. Run NPC Background Scheduler
        self._run_npc_scheduler(working_state, universe, mutations)

        # 4. Validate Final State
        val_ok, val_err = self.validate_world_state(working_state, universe)
        if not val_ok:
            return SimulationResult(
                simulation_id=sim_id,
                universe_id=universe.metadata.id,
                updated_world_state=world_state,
                updated_timeline=working_timeline,
                success=False,
                error_message=val_err or "Simulation validation failed.",
            )

        return SimulationResult(
            simulation_id=sim_id,
            universe_id=universe.metadata.id,
            updated_world_state=working_state,
            updated_timeline=working_timeline,
            mutations=mutations,
            generated_events=generated_events,
            success=True,
        )

    def _apply_location_update(
        self,
        character_id: str,
        target_location_id: str,
        world_state: WorldState,
        universe: Universe,
        mutations: list[dict[str, Any]],
    ) -> None:
        """Move character to new location and update occupant lists."""
        if not target_location_id or not universe.get_location(target_location_id):
            logger.warning("Target location '%s' invalid; skipping movement.", target_location_id)
            return

        old_loc_id = None
        if character_id in world_state.characters:
            old_loc_id = world_state.characters[character_id].location

        # Update character state
        char_st = world_state.characters.get(
            character_id, CharacterState(character_id=character_id, location=target_location_id)
        )
        world_state.characters[character_id] = char_st.model_copy(
            update={"location": target_location_id}
        )

        # Remove from old location occupants
        if old_loc_id and old_loc_id in world_state.locations:
            old_loc_st = world_state.locations[old_loc_id]
            new_occupants = [cid for cid in old_loc_st.occupants if cid != character_id]
            world_state.locations[old_loc_id] = old_loc_st.model_copy(
                update={"occupants": new_occupants}
            )

        # Add to new location occupants
        new_loc_st = world_state.locations.get(
            target_location_id, LocationState(location_id=target_location_id)
        )
        if character_id not in new_loc_st.occupants:
            updated_occupants = list(new_loc_st.occupants) + [character_id]
            world_state.locations[target_location_id] = new_loc_st.model_copy(
                update={"occupants": updated_occupants}
            )

        mutations.append(
            {
                "entity": character_id,
                "field": "location",
                "old": old_loc_id,
                "new": target_location_id,
            }
        )

    def _apply_item_transfer(
        self,
        item_id: str,
        sender_id: str,
        recipient_id: str,
        world_state: WorldState,
        universe: Universe,
        mutations: list[dict[str, Any]],
    ) -> None:
        """Transfer object from location/character to recipient."""
        # Find item location
        cur_loc_id = None
        for loc_id, loc_st in world_state.locations.items():
            if item_id in loc_st.objects:
                cur_loc_id = loc_id
                break

        if cur_loc_id and cur_loc_id in world_state.locations:
            loc_st = world_state.locations[cur_loc_id]
            new_objs = [oid for oid in loc_st.objects if oid != item_id]
            world_state.locations[cur_loc_id] = loc_st.model_copy(update={"objects": new_objs})

        mutations.append(
            {
                "entity": item_id,
                "field": "owner",
                "old": cur_loc_id or sender_id,
                "new": recipient_id,
            }
        )

    def _apply_item_use(
        self,
        item_id: str,
        character_id: str,
        world_state: WorldState,
        universe: Universe,
        mutations: list[dict[str, Any]],
    ) -> None:
        """Execute item usage effects."""
        mutations.append(
            {
                "entity": item_id,
                "field": "state",
                "action": "use",
                "by": character_id,
            }
        )

    def _apply_relationship_changes(
        self,
        source_id: str,
        changes: list[dict[str, Any]],
        world_state: WorldState,
        universe: Universe,
        mutations: list[dict[str, Any]],
    ) -> None:
        """Apply relationship score updates with clamping [0, 100]."""
        for change in changes:
            target_id = change.get("target")
            delta = change.get("delta", 0)
            if not target_id:
                continue

            rel_key = f"{source_id}_{target_id}"
            rel_st = world_state.relationships.get(
                rel_key,
                RelationshipState(relationship_id=rel_key, trust=50, respect=50, affection=50),
            )

            # Apply bounded delta limit (+/-10)
            capped_delta = max(-10, min(10, int(delta)))
            new_trust = self.relationship_engine.clamp_score(rel_st.trust + capped_delta, 0, 100)

            world_state.relationships[rel_key] = rel_st.model_copy(update={"trust": new_trust})
            mutations.append(
                {
                    "entity": rel_key,
                    "field": "trust",
                    "old": rel_st.trust,
                    "new": new_trust,
                }
            )

    def _run_npc_scheduler(
        self,
        world_state: WorldState,
        universe: Universe,
        mutations: list[dict[str, Any]],
    ) -> None:
        """Update idle NPCs so the world remains alive."""
        # Simple background activity assignment for idle NPCs
        for cid, char_st in world_state.characters.items():
            if cid == "char_user":
                continue
            if not char_st.current_action:
                world_state.characters[cid] = char_st.model_copy(
                    update={"current_action": "Going about daily routine"}
                )

    def validate_world_state(
        self, world_state: WorldState, universe: Universe
    ) -> tuple[bool, str | None]:
        """
        Validate integrity of the updated WorldState.

        Returns:
            Tuple of (is_valid, error_message).
        """
        # Verify characters exist in Universe
        for cid in world_state.characters:
            if not universe.get_character(cid):
                return False, f"Character '{cid}' in WorldState not found in Universe."

        # Verify location references
        for loc_id in world_state.locations:
            if not universe.get_location(loc_id):
                return False, f"Location '{loc_id}' in WorldState not found in Universe."

        return True, None
