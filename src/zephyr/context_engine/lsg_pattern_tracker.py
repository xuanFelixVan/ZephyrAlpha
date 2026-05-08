"""lsg_pattern_tracker.py — LSG 模式逃逸追踪 (B20, DD94, TASK-017)"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class LSGRejectionPattern:
    reason_code: str
    count: int
    same_pattern_3x: bool
    cross_session_10x: bool
    action_needed: str


class LSGPatternTracker:
    """LSG rejection_reason_code tracking; 3x→retry; 10x cross-session → escalate (DD94)."""
    def __init__(self) -> None:
        self._counters: Counter[str] = Counter()
        self._cross_session: Counter[str] = Counter()

    def track_rejection(self, reason_code: str) -> LSGRejectionPattern:
        self._counters[reason_code] += 1
        count = self._counters[reason_code]
        return LSGRejectionPattern(
            reason_code=reason_code,
            count=count,
            same_pattern_3x=count >= 3,
            cross_session_10x=self._cross_session.get(reason_code, 0) >= 10,
            action_needed="rebuild" if count >= 3 else "retry" if count >= 2 else "none",
        )
