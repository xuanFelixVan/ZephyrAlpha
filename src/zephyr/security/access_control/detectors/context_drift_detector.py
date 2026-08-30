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
# [A_module] module_id=MOD-INF-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ContextDriftDetector — 上下文漂移与范围蔓延检测.

依据蓝图 MOD-INF-018 §3:
- 记录 agent 操作序列
- 检测操作是否超出基线范围（scope creep）

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: context_drift_detector.py
# 层: 算法
# - id: A1
#   name_zh: ① ContextDriftDetector
#   name_en: ContextDriftDetector
#   intro: 上下文漂移检测器 — 基于操作序列检测范围蔓延.
#   desc: 上下文漂移检测器 — 基于操作序列检测范围蔓延.；公共方法（定义序）: contexts, record_operation, reset, detect_scope_creep；源码 L60-L135
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ContextDriftDetector
#   downstream: tests/agent_rbac/test_redteam_adversarial.py
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

# Cap for recent_violations list — limits response size for high-violation agents.
_RECENT_VIOLATIONS_CAP = 5


class ContextDriftDetector:
    """上下文漂移检测器 — 基于操作序列检测范围蔓延."""

    def __init__(self) -> None:
        # Primary attribute name per test contract (test_context_drift_detector.py).
        # `_operations` is kept as a read-only backward-compat alias via __getattr__.
        self._contexts: dict[str, list[str]] = defaultdict(list)

    @property
    def contexts(self) -> dict[str, list[str]]:
        """只读：contexts（Stage 4 公共化）。"""
        return self._contexts

    @contexts.setter
    def contexts(self, value):
        """写入：contexts（Stage 4 公共化）。"""
        self._contexts = value

    def __getattr__(self, name: str) -> Any:
        # Backward-compat: `_operations` -> `_contexts` (legacy callers/tests).
        if name == "_operations":
            return self.__dict__.get("_contexts")
        raise AttributeError(name)

    def record_operation(self, agent_id: str, operation: str) -> None:
        self._contexts[agent_id].append(operation)

    def reset(self, agent_id: str) -> None:
        """Clear recorded operations for a specific agent.

        Safe to call for an agent that has no recorded operations (no-op).
        """
        self._contexts.pop(agent_id, None)

    def detect_scope_creep(
        self,
        agent_id: str,
        baseline_operations: list[str],
        window: int = 50,
    ) -> dict:
        """Detect scope creep for an agent over a sliding window of operations.

        Returns a dict with keys:
          - exceeded (bool): True if any out-of-scope operation detected.
          - violations (int): count of out-of-scope ops in window.
          - total_ops (int): count of ops examined in window.
          - violation_ratio (float): violations / total_ops (0.0 if no ops).
          - recent_violations (list[str]): most recent violation op names (<=5).
          - window (int): effective window size used.
          - out_of_scope_count (int): alias for violations (backward-compat).
          - recent_total (int): alias for total_ops (backward-compat).

        Never raises; returns {"exceeded": False, ...zeros} for unknown agent.
        """
        ops = self._contexts.get(agent_id, [])
        effective_window = window if window >= 1 else 1
        recent = ops[-effective_window:] if len(ops) > effective_window else ops[:]
        baseline_set = set(baseline_operations)
        recent_violations = [op for op in recent if op not in baseline_set]
        violations = len(recent_violations)
        total_ops = len(recent)
        # Security stance: any out-of-scope operation = scope creep exceeded.
        # The previous `threshold = max(1, int(window * 0.5))` was too lax and
        # allowed agents to perform many unauthorized ops before tripping.
        exceeded = violations > 0
        violation_ratio = violations / total_ops if total_ops > 0 else 0.0
        return {
            "exceeded": exceeded,
            "violations": violations,
            "total_ops": total_ops,
            "violation_ratio": violation_ratio,
            "recent_violations": recent_violations[-_RECENT_VIOLATIONS_CAP:],
            "window": effective_window,
            "out_of_scope_count": violations,  # backward-compat
            "recent_total": total_ops,  # backward-compat
        }
