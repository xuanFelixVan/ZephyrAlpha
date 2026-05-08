"""session_learner.py — 在线学习 (DD114, TASK-020)"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class LearningEvent:
    ke_id: str
    cited: bool
    success: bool
    timestamp: str


class SessionLearner:
    """Per-session Reinforcement Learning: citation + outcome (DD114)."""
    def __init__(self) -> None:
        self._events: list[LearningEvent] = []
        self._ke_weights: dict[str, float] = {}

    def record(self, ke_id: str, cited: bool, success: bool, timestamp: str = "") -> None:
        self._events.append(LearningEvent(ke_id=ke_id, cited=cited, success=success, timestamp=timestamp))
        delta = 0.1 if cited and success else (-0.05 if not cited else 0.0)
        self._ke_weights[ke_id] = max(0.0, min(1.0, self._ke_weights.get(ke_id, 0.5) + delta))

    def get_weight(self, ke_id: str) -> float:
        return self._ke_weights.get(ke_id, 0.5)
