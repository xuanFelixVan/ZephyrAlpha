# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.governance.capacity_budget
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
全局容量预算控制器（Capacity Budget Controller）

依据：MOD-MASTER-002 蓝图 §五 全局容量预算
实现并发任务上限 + WIP Limit + 线程池配额。

规则：
1. max_concurrent_tasks: 硬上限，超限任务自动 QUEUED
2. WIP Limit: 每系统独立线程池容量预算
3. 任务完成 -> 从 QUEUED 队首出队

# [ALGO_FLOW] external: docs/03_modules/_domain_orchestrator/algo_flow/capacity_budget.yaml
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Final

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SystemPool(str, Enum):
    ORCHESTRATOR = "orchestrator"
    SCRIPT_SYSTEM = "script_system"
    GATES = "gate_engine"
    CE = "context-engine"
    PIPELINE = "pipeline"
    FLE = "feedback-loop"
    VMS = "vector-memory"
    DB = "database"
    LSG = "llm-security"
    TELEMETRY = "system-telemetry"
    MCP = "mcp_servers"


DEFAULT_POOL_QUOTAS: Final[dict[SystemPool, int]] = {
    SystemPool.ORCHESTRATOR: 16,
    SystemPool.SCRIPT_SYSTEM: 4,
    SystemPool.GATES: 4,
    SystemPool.CE: 4,
    SystemPool.PIPELINE: 4,
    SystemPool.FLE: 4,
    SystemPool.VMS: 4,
    SystemPool.DB: 4,
    SystemPool.LSG: 4,
    SystemPool.TELEMETRY: 4,
    SystemPool.MCP: 2,
}


class CapacityBudget(BaseModel):
    max_concurrent_tasks: int = Field(default=64, gt=0)
    wip_limit_per_system: dict[str, int] = Field(
        default_factory=lambda: {k.value: v for k, v in DEFAULT_POOL_QUOTAS.items()}
    )


class CapacityState(BaseModel):
    active_tasks: int = 0
    queued_tasks: int = 0
    system_active: dict[str, int] = Field(default_factory=lambda: {k.value: 0 for k in SystemPool})
    max_concurrent: int = 64
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))


class CapacityBudgetController:
    def __init__(self, max_concurrent_tasks: int = 64):
        self._budget = CapacityBudget(max_concurrent_tasks=max_concurrent_tasks)
        self._state = CapacityState(max_concurrent=max_concurrent_tasks)
        self._queue: list[str] = []

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def budget(self):
        """只读：budget（Stage 4 公共化）。"""
        return self._budget

    @budget.setter
    def budget(self, value):
        """写入：budget（Stage 4 公共化）。"""
        self._budget = value

    @property
    def state(self) -> CapacityState:
        return self._state

    @property
    def max_concurrent(self) -> int:
        return self._budget.max_concurrent_tasks

    def can_accept(self, system: str) -> bool:
        if self._state.active_tasks >= self._budget.max_concurrent_tasks:
            return False

        key = self._normalize_key(system)
        quota = self._budget.wip_limit_per_system.get(key)
        if quota is None:
            return True  # 无声明配额=放行（不臆造配额；枚举系统默认预算已含全量配额）

        current = self._state.system_active.get(key, 0)
        return current < quota

    def try_accept(self, task_id: str, system: str) -> bool:
        if self.can_accept(system):
            self._accept(task_id, system)
            return True

        self._queue.append(task_id)
        self._state.queued_tasks = len(self._queue)
        return False

    def _accept(self, task_id: str, system: str) -> None:
        self._state.active_tasks += 1
        key = self._normalize_key(system)
        self._state.system_active[key] = self._state.system_active.get(key, 0) + 1
        self._state.last_updated = datetime.now(UTC)

    def release(self, task_id: str, system: str) -> str | None:
        self._state.active_tasks = max(0, self._state.active_tasks - 1)
        key = self._normalize_key(system)
        self._state.system_active[key] = max(0, self._state.system_active.get(key, 0) - 1)

        self._state.last_updated = datetime.now(UTC)

        if self._queue:
            next_task = self._queue.pop(0)
            self._state.queued_tasks = len(self._queue)
            self._accept(next_task, system)
            return next_task
        return None

    def get_queue_position(self, task_id: str) -> int:
        try:
            return self._queue.index(task_id) + 1
        except ValueError:
            return -1

    @staticmethod
    def _normalize_key(system: str) -> str:
        """枚举成员归一取 value；否则原样用作池键——注册表泳道（default/heavy/realtime/
        intraday_* 等）由 WIP 供给后即可强制，向后兼容枚举路径。"""
        try:
            return SystemPool(system).value
        except ValueError:
            return system

    def get_pool_quota(self, system: str) -> int:
        key = self._normalize_key(system)
        return int(self._budget.wip_limit_per_system.get(key, 4))
