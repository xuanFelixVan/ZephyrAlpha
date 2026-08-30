# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.lifecycle.state_propagation
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
全局状态传播链（State Propagation Chain）

依据：MOD-MASTER-002 蓝图 §四 全局状态传播链 (CT-ORC-DB)
TaskCard 状态变更 -> 所有关联系统得到通知。

传播规则：
- PENDING -> IN_PROGRESS: 通知 Gates + FLE
- IN_PROGRESS -> COMPLETED: 通知 VMS 向量化 + db 持久化
- IN_PROGRESS -> BLOCKED: 通知 Gates 检查阻塞 + FLE 记录
- IN_PROGRESS -> FAILED: 通知 FLE + db 持久化

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: state_propagation.py
# 层: 算法
# - id: A1
#   name_zh: ① StatePropagator
#   name_en: StatePropagator
#   intro: class StatePropagator 源码 L117-L157
#   desc: 公共方法（定义序）: propagate, get_events, get_events_for_task, get_notifiable_targets；源码 L117-L157
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: StatePropagator
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Final

from pydantic import BaseModel, Field


class PropagationTarget(str, Enum):
    GATES = "gates"
    VMS = "vector-memory"
    FLE = "feedback-loop"
    DB = "database"
    ORCHESTRATOR = "orchestrator"


PROPAGATION_RULES: Final[dict[str, dict[str, list[PropagationTarget]]]] = {
    # P4 修复（2026-07-05）：迁移键派生自 TaskStatus SSoT
    # 真源：zephyr.gov_enforcement.rule_enforcement.task_types.TaskStatus
    # 合法状态值（大写）：PENDING/CREATED/LOCKED/ASSIGNED/READY/IN_PROGRESS/
    #   REVIEWING/COMPLETED/VERIFIED/FAILED/BLOCKED/WAITING/RETRY/CANCELLED
    # 迁移键格式："FROM->TO"，FROM/TO 必须是 SSoT 中的合法状态值。
    # 合法迁移边定义在 TaskRepository.transition() 中，本表仅定义通知传播目标。
    "PENDING->IN_PROGRESS": {
        "sources": [],  # 改为直接映射
        "notify": [PropagationTarget.GATES, PropagationTarget.FLE],
    },
    "IN_PROGRESS->COMPLETED": {
        "notify": [PropagationTarget.VMS, PropagationTarget.DB, PropagationTarget.FLE],
    },
    "IN_PROGRESS->BLOCKED": {
        "notify": [PropagationTarget.GATES, PropagationTarget.FLE],
    },
    "IN_PROGRESS->FAILED": {
        "notify": [PropagationTarget.FLE, PropagationTarget.DB],
    },
    "COMPLETED->VERIFIED": {
        "notify": [PropagationTarget.DB, PropagationTarget.FLE],
    },
    "BLOCKED->IN_PROGRESS": {
        "notify": [PropagationTarget.GATES, PropagationTarget.FLE],
    },
    "BLOCKED->CANCELLED": {
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
        transition_key = f"{old_status}->{new_status}"
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
        transition_key = f"{old_status}->{new_status}"
        rule = PROPAGATION_RULES.get(transition_key)
        if rule is None:
            return []
        return [t.value for t in rule["notify"]]
