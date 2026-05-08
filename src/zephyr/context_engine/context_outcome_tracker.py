"""context_outcome_tracker.py — 因果链追踪 (B14, DD88, TASK-017)"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import Counter


@dataclass
class ContextOutcomeLink:
    context_block_id: str
    agent_actions: list[str]
    action_successes: list[bool]
    success_rate: float = 0.0
    suspect: bool = False


class ContextOutcomeTracker:
    """ContextBlock → Agent Action → Action Success 三级因果关联 (DD88)."""
    def __init__(self) -> None:
        self._links: dict[str, ContextOutcomeLink] = {}

    def record(self, context_id: str, actions: list[str], successes: list[bool]) -> ContextOutcomeLink:
        rate = sum(successes) / max(1, len(successes))
        link = ContextOutcomeLink(
            context_block_id=context_id,
            agent_actions=actions,
            action_successes=successes,
            success_rate=round(rate, 3),
            suspect=rate < 0.5,
        )
        self._links[context_id] = link
        return link

    def low_success_ke(self) -> list[str]:
        return [k for k, v in self._links.items() if v.suspect]
