# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.feedback_collector
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.integration.shared.schema.schemas
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_feedback_collector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
FeedbackCollector: collect task execution feedback
===================================================
Task ID : T-2-29 (C54)
safety_level : L
Depends : none

Collects feedback from task execution, supporting:
  - Numeric scores (1-5 scale)
  - Free-text comments
  - Structured tags (e.g. "slow", "accurate", "needs-review")

Feedback entries are stored in-memory and can be flushed to disk
as JSON for downstream analysis or audit logging.
"""

from __future__ import annotations
from zephyr.shared.io.serialization import dumps

import json
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, field_validator

from zephyr.integration.shared.schema.schemas import BASE_CONFIG
from zephyr.shared.utils.time_utils import now_utc

__all__ = [
    "FeedbackCollector",
    "FeedbackEntry",
    "FeedbackSummary",
]

_VALID_SCORE_RANGE = (1, 5)


class FeedbackEntry(BaseModel):
    model_config = BASE_CONFIG

    entry_id: str = Field(min_length=1, description="Unique feedback entry ID")
    task_id: str = Field(min_length=1, description="Associated task ID")
    score: int = Field(ge=1, le=5, description="Numeric score 1-5")
    comment: str = Field(default="", max_length=2000, description="Free-text comment")
    tags: list[str] = Field(default_factory=list, description="Structured tags")
    created_at: datetime = Field(description="Entry creation timestamp")

    @field_validator("tags")
    @classmethod
    def tags_no_duplicates(cls, v: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for tag in v:
            if tag not in seen:
                seen.add(tag)
                result.append(tag)
        return result


class FeedbackSummary(BaseModel):
    model_config = BASE_CONFIG

    task_id: str = Field(min_length=1, description="Task ID being summarized")
    count: int = Field(ge=0, description="Total number of feedback entries")
    average_score: float = Field(ge=0.0, le=5.0, description="Average score (0.0 when no entries)")
    tag_frequencies: dict[str, int] = Field(default_factory=dict, description="Tag occurrence counts")
    latest_comment: str = Field(default="", description="Most recent comment")


class FeedbackCollector:
    """Collect and manage task execution feedback.

    Parameters
    ----------
    store_path : Path | None
        Optional file path for persisting feedback as JSON.
        If None, feedback is kept in-memory only.
    """

    def __init__(self, store_path: Path | None = None) -> None:
        self._entries: list[FeedbackEntry] = []
        self._store_path = store_path
        self._next_id: int = 1

    def add(
        self,
        task_id: str,
        score: int,
        comment: str = "",
        tags: list[str] | None = None,
        created_at: datetime | None = None,
    ) -> FeedbackEntry:
        entry = FeedbackEntry(
            entry_id=f"FB-{self._next_id:04d}",
            task_id=task_id,
            score=score,
            comment=comment,
            tags=tags or [],
            created_at=created_at or now_utc(),
        )
        self._entries.append(entry)
        self._next_id += 1
        return entry

    def get_entries(self, task_id: str | None = None) -> list[FeedbackEntry]:
        if task_id is None:
            return list(self._entries)
        return [e for e in self._entries if e.task_id == task_id]

    def summarize(self, task_id: str) -> FeedbackSummary:
        entries = self.get_entries(task_id)
        if not entries:
            return FeedbackSummary(
                task_id=task_id,
                count=0,
                average_score=0.0,
                tag_frequencies={},
                latest_comment="",
            )
        avg = sum(e.score for e in entries) / len(entries)
        tag_freq: dict[str, int] = {}
        for e in entries:
            for tag in e.tags:
                tag_freq[tag] = tag_freq.get(tag, 0) + 1
        latest = entries[-1].comment
        return FeedbackSummary(
            task_id=task_id,
            count=len(entries),
            average_score=round(avg, 2),
            tag_frequencies=tag_freq,
            latest_comment=latest,
        )

    def flush(self) -> int:
        if self._store_path is None:
            return 0
        data = [e.model_dump(mode="json") for e in self._entries]
        self._store_path.parent.mkdir(parents=True, exist_ok=True)
        self._store_path.write_text(
            dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return len(self._entries)

    def load(self) -> int:
        if self._store_path is None or not self._store_path.exists():
            return 0
        raw = self._store_path.read_text(encoding="utf-8")
        items = json.loads(raw)
        loaded: list[FeedbackEntry] = []
        max_id = self._next_id
        for item in items:
            entry = FeedbackEntry.model_validate(item)
            loaded.append(entry)
            num_part = entry.entry_id.split("-")[1]
            numeric_id = int(num_part)
            if numeric_id >= max_id:
                max_id = numeric_id + 1
        self._entries = loaded
        self._next_id = max_id
        return len(loaded)

    def clear(self) -> int:
        count = len(self._entries)
        self._entries.clear()
        self._next_id = 1
        return count

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    @property
    def store_path(self) -> Path | None:
        return self._store_path


class ActionResult:
    def __init__(self, action="", success=True, duration=0.0, error=None, metadata=None):
        self.action = action
        self.success = success
        self.duration = duration
        self.error = error
        self.metadata = metadata or {}


class FeedbackChannel:
    DIRECT = "DIRECT"
    OBSERVATION = "OBSERVATION"
    METRIC = "METRIC"
    ALERT = "ALERT"
    USER = "USER"


class OwnerResponse:
    def __init__(self, action="", approved=False, reason="", timestamp=None):
        self.action = action
        self.approved = approved
        self.reason = reason
        self.timestamp = timestamp


class OwnerAck:
    def __init__(self, ack_id="", owner="", action="", timestamp=None):
        self.ack_id = ack_id
        self.owner = owner
        self.action = action
        self.timestamp = timestamp
