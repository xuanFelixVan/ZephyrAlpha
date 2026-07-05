# [BLUEPRINT] MOD-INF-018 | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §3
# [MODULE] zephyr.security.access_control.intent_binder
# [DOMAIN] D_SECURITY
# [DEPENDENCIES]
# [CONSUMERS] tests/agent_rbac/test_redteam_adversarial.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] declare is idempotent per agent_id (overwrites); check_drift returns bool
# [MODIFY-GUARD] blueprint.md §3
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check_drift never raises; returns False when agent unknown or no actual operations recorded
# [TESTS] tests/agent_rbac/test_redteam_adversarial.py
# [A_module] module_id=MOD-SEC_intent_binder | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""IntentBinder — 意图绑定与漂移检测.

依据蓝图 MOD-INF-018 §3:
- 声明 agent 对文件的任务意图与预期操作集
- 检测实际操作是否偏离声明意图（IBAC 横切面）
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class IntentDeclaration:
    """意图声明 — agent 对某文件的任务与预期操作."""

    agent_id: str = ""
    file: str = ""
    task: str = ""
    expected_operations: list[str] = field(default_factory=list)
    actual_operations: list[str] = field(default_factory=list)
    state: str = ""


class IntentState:
    """意图状态枚举 — DECLARED / ACTIVE / DRIFTED / FULFILLED / COMPLETED."""

    DECLARED = "declared"
    ACTIVE = "active"
    DRIFTED = "drifted"
    FULFILLED = "fulfilled"
    COMPLETED = "completed"


class IntentBinder:
    """意图绑定器 — 管理声明意图与漂移检测."""

    def __init__(self) -> None:
        self._declarations: dict[str, IntentDeclaration] = {}

    def declare(
        self,
        agent_id: str,
        file: str,
        task: str,
        expected_operations: list[str] | None = None,
    ) -> IntentDeclaration:
        decl = IntentDeclaration(
            agent_id=agent_id,
            file=file,
            task=task,
            expected_operations=list(expected_operations or []),
            state=IntentState.ACTIVE,
        )
        self._declarations[agent_id] = decl
        return decl

    def verify(self, agent_id: str, operation: str) -> bool:
        """验证操作是否在声明意图范围内，并记录实际操作."""
        decl = self._declarations.get(agent_id)
        if decl is None:
            return False
        decl.actual_operations.append(operation)
        return operation in decl.expected_operations

    def close(self, agent_id: str) -> None:
        """关闭意图，标记为 COMPLETED."""
        decl = self._declarations.get(agent_id)
        if decl is not None:
            decl.state = IntentState.COMPLETED

    def get_active_intent(self, agent_id: str) -> IntentDeclaration | None:
        """获取 agent 的活动意图声明."""
        return self._declarations.get(agent_id)

    def record_actual(self, agent_id: str, operation: str) -> None:
        decl = self._declarations.get(agent_id)
        if decl is not None:
            decl.actual_operations.append(operation)

    def check_drift(self, agent_id: str) -> bool:
        decl = self._declarations.get(agent_id)
        if decl is None:
            return False
        for op in decl.actual_operations:
            if op not in decl.expected_operations:
                return True
        return False


__all__ = [
    "IntentBinder",
    "IntentDeclaration",
    "IntentState",
]
