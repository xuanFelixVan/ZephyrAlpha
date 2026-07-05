# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.detectors.context_drift_detector
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] detect_scope_creep returns dict with "exceeded" bool key; window >= 1
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] detect_scope_creep never raises; returns {"exceeded": False} for unknown agent
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_context_drift_detector | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ContextDriftDetector — 上下文漂移与范围蔓延检测.

依据蓝图 MOD-INF-018 §3:
- 记录 agent 操作序列
- 检测操作是否超出基线范围（scope creep）
"""

from __future__ import annotations

from collections import defaultdict


class ContextDriftDetector:
    """上下文漂移检测器 — 基于操作序列检测范围蔓延."""

    def __init__(self) -> None:
        self._operations: dict[str, list[str]] = defaultdict(list)

    def record_operation(self, agent_id: str, operation: str) -> None:
        self._operations[agent_id].append(operation)

    def detect_scope_creep(
        self,
        agent_id: str,
        baseline_operations: list[str],
        window: int = 50,
    ) -> dict:
        ops = self._operations.get(agent_id, [])
        effective_window = window if window >= 1 else 1
        recent = ops[-effective_window:] if len(ops) > effective_window else ops[:]
        baseline_set = set(baseline_operations)
        out_of_scope = sum(1 for op in recent if op not in baseline_set)
        threshold = max(1, int(effective_window * 0.5))
        exceeded = out_of_scope >= threshold
        return {
            "exceeded": exceeded,
            "out_of_scope_count": out_of_scope,
            "window": effective_window,
            "recent_total": len(recent),
        }


__all__ = [
    "ContextDriftDetector",
]
