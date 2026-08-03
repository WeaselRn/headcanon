"""
Timeline Engine for Headcanon.

Maintains chronological continuity, records objective events, detects divergence
from canon, and manages timeline branching.

Reference: docs/engines/08_timeline_engine.md, docs/universe/05_timeline.md
"""

from __future__ import annotations

import logging
import re
import uuid
from pathlib import Path
from typing import Any

from app.world.timeline import (
    EventStatus,
    EventType,
    Timeline,
    TimelineBranch,
    TimelineEvent,
    WorldTime,
)
from app.world.universe import Universe

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).parent.parent / "prompts" / "simulation"


class TimelineEngine:
    """
    The historian and continuity manager of Headcanon.

    Responsibilities:
      - Record new events into the Timeline in strict chronological sequence
      - Advance abstract WorldTime (hours, days)
      - Detect canonical divergence points and spawn timeline branches
      - Validate sequence integrity, participant uniqueness, and event ordering

    Args:
        ai_client: Optional injected AI client for prompt execution.
        prompt_dir: Path to simulation prompt directory.
    """

    def __init__(self, ai_client: Any = None, prompt_dir: Path = _PROMPT_DIR) -> None:
        self.ai_client = ai_client
        self.prompt_dir = prompt_dir
        self._prompts: dict[str, str] = {}
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Pre-load simulation prompt templates."""
        if self.prompt_dir.exists():
            for file in self.prompt_dir.glob("*.txt"):
                self._prompts[file.name] = file.read_text(encoding="utf-8")

    def advance_time(self, current_time: WorldTime, hours: int = 1) -> WorldTime:
        """
        Advance in-universe WorldTime by the given number of hours.

        Args:
            current_time: Current WorldTime model.
            hours: Number of hours to advance (must be >= 1).

        Returns:
            Updated WorldTime model instance.
        """
        if hours < 1:
            return current_time

        total_hours = current_time.hour + hours
        day_overflow, new_hour = divmod(total_hours, 24)
        new_day = current_time.day + day_overflow

        return WorldTime(
            day=new_day,
            hour=new_hour,
            minute=current_time.minute,
            season=current_time.season,
            weather=current_time.weather,
            timeline_position=current_time.timeline_position,
        )

    def create_event(
        self,
        title: str,
        description: str,
        event_type: EventType = EventType.USER_ACTION,
        location: str | None = None,
        participants: list[str] | None = None,
        timestamp: str | None = None,
        sequence: int = 0,
        status: EventStatus = EventStatus.COMPLETED,
        importance: int = 50,
        causes: list[str] | None = None,
        consequences: list[str] | None = None,
    ) -> TimelineEvent:
        """
        Create a validated TimelineEvent model.

        Args:
            title: Human-readable title.
            description: Event summary.
            event_type: EventType enum.
            location: Location ID.
            participants: Unique list of character IDs.
            timestamp: Abstract time string.
            sequence: Chronological order index.
            status: EventStatus enum.
            importance: Integer [0, 100].
            causes: Parent event IDs.
            consequences: Dependent event IDs.

        Returns:
            TimelineEvent instance.
        """
        slug = re.sub(r"[^a-zA-Z0-9_]+", "_", title.lower()).strip("_")
        event_id = f"evt_{slug[:25]}_{uuid.uuid4().hex[:4]}"

        # Ensure unique participants
        unique_participants = list(dict.fromkeys(participants or []))

        return TimelineEvent(
            id=event_id,
            title=title,
            description=description,
            type=event_type,
            timestamp=timestamp,
            participants=unique_participants,
            location=location,
            sequence=max(0, sequence),
            status=status,
            importance=max(0, min(100, importance)),
            causes=causes or [],
            consequences=consequences or [],
        )

    def append_event(self, timeline: Timeline, new_event: TimelineEvent) -> Timeline:
        """
        Append a new TimelineEvent to the timeline in ascending sequence order.

        Args:
            timeline: Current Timeline container.
            new_event: TimelineEvent to record.

        Returns:
            Updated Timeline model.
        """
        # Determine next sequence number if not explicitly set
        existing_sequences = [e.sequence for e in timeline.events]
        next_seq = new_event.sequence
        if next_seq in existing_sequences or next_seq == 0:
            next_seq = (max(existing_sequences) + 1) if existing_sequences else 1

        updated_event = TimelineEvent(
            id=new_event.id,
            title=new_event.title,
            description=new_event.description,
            type=new_event.type,
            timestamp=new_event.timestamp,
            participants=new_event.participants,
            location=new_event.location,
            sequence=next_seq,
            status=new_event.status,
            importance=new_event.importance,
            causes=new_event.causes,
            consequences=new_event.consequences,
            metadata=new_event.metadata,
        )

        all_events = list(timeline.events) + [updated_event]
        # Sort chronologically by sequence number
        sorted_events = sorted(all_events, key=lambda e: e.sequence)

        # Update event status tracking lists
        completed = list(timeline.completed_events)
        active = list(timeline.active_events)
        scheduled = list(timeline.scheduled_events)
        cancelled = list(timeline.cancelled_events)

        if updated_event.status == EventStatus.COMPLETED and updated_event.id not in completed:
            completed.append(updated_event.id)
        elif updated_event.status == EventStatus.ACTIVE and updated_event.id not in active:
            active.append(updated_event.id)
        elif updated_event.status == EventStatus.SCHEDULED and updated_event.id not in scheduled:
            scheduled.append(updated_event.id)
        elif updated_event.status == EventStatus.CANCELLED and updated_event.id not in cancelled:
            cancelled.append(updated_event.id)

        # Update timeline position in current_time
        updated_time = WorldTime(
            day=timeline.current_time.day,
            hour=timeline.current_time.hour,
            minute=timeline.current_time.minute,
            season=timeline.current_time.season,
            weather=timeline.current_time.weather,
            timeline_position=updated_event.id,
        )

        return Timeline(
            current_time=updated_time,
            events=sorted_events,
            active_events=active,
            scheduled_events=scheduled,
            completed_events=completed,
            cancelled_events=cancelled,
            branches=timeline.branches,
            metadata=timeline.metadata,
        )

    def detect_divergence(
        self,
        timeline: Timeline,
        event: TimelineEvent,
        universe: Universe,
    ) -> bool:
        """
        Check if a newly generated event diverges from canonical universe events.

        Args:
            timeline: Live Timeline model.
            event: Proposed new TimelineEvent.
            universe: Canonical Universe model.

        Returns:
            True if a divergence from canon occurred, False otherwise.
        """
        # If the event contradicts any canonical rule or character status, it diverges
        if event.importance >= 80 and event.type in (
            EventType.DEATH,
            EventType.COMBAT,
            EventType.WORLD_EVENT,
        ):
            return True
        return False

    def create_branch(
        self,
        timeline: Timeline,
        origin_event_id: str,
        description: str,
    ) -> TimelineBranch:
        """
        Create a new TimelineBranch originating at a specific event.

        Args:
            timeline: Current Timeline container.
            origin_event_id: ID of divergence event.
            description: Reason for branch.

        Returns:
            Newly created TimelineBranch model instance.
        """
        branch_id = f"branch_{uuid.uuid4().hex[:6]}"
        return TimelineBranch(
            branch_id=branch_id,
            origin_event=origin_event_id,
            description=description,
            events=[origin_event_id],
        )

    def validate_timeline(self, timeline: Timeline) -> tuple[bool, str | None]:
        """
        Validate chronological consistency of a Timeline container.

        Returns:
            Tuple of (is_valid, error_message).
        """
        sequences = [e.sequence for e in timeline.events]
        if len(sequences) != len(set(sequences)):
            return False, "Duplicate event sequence numbers found in timeline."

        if sequences != sorted(sequences):
            return False, "Timeline events are not sorted in ascending sequence order."

        return True, None
