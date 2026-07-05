# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.trading.orchestrator.governance.capacity_budget
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
# [A_module] module_id=MOD-ORC_capacity_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
全局容量预算控制器（Capacity Budget Controller）

依据：MOD-MASTER-002 蓝图 §五 全局容量预算
实现并发任务上限 + WIP Limit + 线程池配额。

规则：
1. max_concurrent_tasks: 硬上限，超限任务自动 QUEUED
2. WIP Limit: 每系统独立线程池容量预算
3. 任务完成 → 从 QUEUED 队首出队
"""

from __future__ import annotations

import logging

from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SystemPool(str, Enum):
    ORCHESTRATOR = "orchestrator"
    SCRIPT_SYSTEM = "script_system"
    KB = "knowledge_base"
    GATES = "gate_engine"
    CE = "context-engine"
    PIPELINE = "pipeline"
    FLE = "feedback-loop"
    VMS = "vector-memory"
    DB = "database"
    LSG = "llm-security"
    TELEMETRY = "system-telemetry"
    MCP = "mcp_servers"


DEFAULT_POOL_QUOTAS: dict[SystemPool, int] = {
    SystemPool.ORCHESTRATOR: 16,
    SystemPool.SCRIPT_SYSTEM: 4,
    SystemPool.KB: 4,
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

    @property
    def state(self) -> CapacityState:
        return self._state

    @property
    def max_concurrent(self) -> int:
        return self._budget.max_concurrent_tasks

    def can_accept(self, system: str) -> bool:
        if self._state.active_tasks >= self._budget.max_concurrent_tasks:
            return False

        pool = self._try_parse_system(system)
        if pool is None:
            return True

        quota = self._budget.wip_limit_per_system.get(pool.value, 4)
        current = self._state.system_active.get(pool.value, 0)
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
        pool = self._try_parse_system(system)
        if pool:
            self._state.system_active[pool.value] += 1
        self._state.last_updated = datetime.now(UTC)

    def release(self, task_id: str, system: str) -> str | None:
        self._state.active_tasks = max(0, self._state.active_tasks - 1)
        pool = self._try_parse_system(system)
        if pool:
            self._state.system_active[pool.value] = max(0, self._state.system_active[pool.value] - 1)

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
    def _try_parse_system(system: str) -> SystemPool | None:
        try:
            return SystemPool(system)
        except ValueError as e:
            logger.warning("_try_parse_system: failed to parse system pool %r (%s: %s)", system, type(e).__name__, e)
            return None

    def get_pool_quota(self, system: str) -> int:
        pool = self._try_parse_system(system)
        if pool is None:
            return 4
        return self._budget.wip_limit_per_system.get(pool.value, 4)
