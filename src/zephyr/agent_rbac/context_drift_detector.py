"""
Context Drift Detector — 对话上下文漂移与Constitution合规审计

MOD-INF-018 §2.15  D-018-23
"""

import re
import time


class ContextDriftDetector:
    def __init__(self) -> None:
        self._contexts: dict[str, list[str]] = {}
        self._drift_threshold: float = 0.5

    def record_operation(self, agent_id: str, operation: str) -> None:
        self._contexts.setdefault(agent_id, []).append(operation)

    def detect_scope_creep(
        self,
        agent_id: str,
        declared_scope: list[str],
        window: int = 50,
    ) -> dict:
        ops = self._contexts.get(agent_id, [])
        recent = ops[-window:] if len(ops) > window else ops
        violations = [op for op in recent if op not in declared_scope]
        ratio = len(violations) / max(len(recent), 1)
        return {
            "agent_id": agent_id,
            "total_ops": len(recent),
            "violations": len(violations),
            "violation_ratio": ratio,
            "exceeded": ratio > self._drift_threshold,
            "recent_violations": violations[-5:] if violations else [],
        }

    def reset(self, agent_id: str) -> None:
        self._contexts.pop(agent_id, None)
