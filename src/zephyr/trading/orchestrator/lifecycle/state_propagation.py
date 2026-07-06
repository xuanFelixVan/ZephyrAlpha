# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.lifecycle.state_propagation
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.trading.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_state_propagation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
全局状态传播链（State Propagation Chain）

依据：MOD-MASTER-002 蓝图 §四 全局状态传播链 (CT-ORC-DB)
TaskCard 状态变更 → 所有关联系统得到通知。

传播规则：
- PENDING → IN_PROGRESS: 通知 Gates + FLE
- IN_PROGRESS → COMPLETED: 通知 VMS 向量化 + db 持久化
- IN_PROGRESS → BLOCKED: 通知 Gates 检查阻塞 + FLE 记录
- IN_PROGRESS → FAILED: 通知 FLE + db 持久化
"""

from __future__ import annotations

from typing import Final
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PropagationTarget(str, Enum):
    GATES = "gates"
    VMS = "vector-memory"
    FLE = "feedback-loop"
    DB = "database"
    KB = "knowledge_base"
    ORCHESTRATOR = "orchestrator"


PROPAGATION_RULES: Final[dict[str, dict[str, list[PropagationTarget]]]] = {
    # P4 修复（2026-07-05）：迁移键派生自 TaskStatus SSoT
    # 真源：zephyr.governance.rule_enforcement.task_types.TaskStatus
    # 合法状态值（大写）：PENDING/CREATED/LOCKED/ASSIGNED/READY/IN_PROGRESS/
    #   REVIEWING/COMPLETED/VERIFIED/FAILED/BLOCKED/WAITING/RETRY/CANCELLED
    # 迁移键格式："FROM→TO"，FROM/TO 必须是 SSoT 中的合法状态值。
    # 合法迁移边定义在 TaskRepository.transition() 中，本表仅定义通知传播目标。
    "PENDING→IN_PROGRESS": {
        "sources": [],  # 改为直接映射
        "notify": [PropagationTarget.GATES, PropagationTarget.FLE],
    },
    "IN_PROGRESS→COMPLETED": {
        "notify": [PropagationTarget.VMS, PropagationTarget.DB, PropagationTarget.FLE],
    },
    "IN_PROGRESS→BLOCKED": {
        "notify": [PropagationTarget.GATES, PropagationTarget.FLE],
    },
    "IN_PROGRESS→FAILED": {
        "notify": [PropagationTarget.FLE, PropagationTarget.DB],
    },
    "COMPLETED→VERIFIED": {
        "notify": [PropagationTarget.DB, PropagationTarget.FLE],
    },
    "BLOCKED→IN_PROGRESS": {
        "notify": [PropagationTarget.GATES, PropagationTarget.FLE],
    },
    "BLOCKED→CANCELLED": {
        "notify": [PropagationTarget.DB, PropagationTarget.FLE],
    },
}


class StatePropagationEvent(BaseModel):
    task_id: str
    old_status: str
    new_status: str
    transition_key: str = ""
    targets: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    payload: dict[str, Any] = Field(default_factory=dict)


class StatePropagator:
    def __init__(self):
        self._events: list[StatePropagationEvent] = []

    def propagate(
        self,
        task_id: str,
        old_status: str,
        new_status: str,
        payload: dict[str, Any] | None = None,
    ) -> list[PropagationTarget]:
        transition_key = f"{old_status}→{new_status}"
        rule = PROPAGATION_RULES.get(transition_key)

        if rule is None:
            return []

        targets = rule["notify"]
        event = StatePropagationEvent(
            task_id=task_id,
            old_status=old_status,
            new_status=new_status,
            transition_key=transition_key,
            targets=[t.value for t in targets],
            payload=payload or {},
        )
        self._events.append(event)
        return list(targets)

    def get_events(self) -> list[StatePropagationEvent]:
        return list(self._events)

    def get_events_for_task(self, task_id: str) -> list[StatePropagationEvent]:
        return [e for e in self._events if e.task_id == task_id]

    def get_notifiable_targets(self, old_status: str, new_status: str) -> list[str]:
        transition_key = f"{old_status}→{new_status}"
        rule = PROPAGATION_RULES.get(transition_key)
        if rule is None:
            return []
        return [t.value for t in rule["notify"]]
