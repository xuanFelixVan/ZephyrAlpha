# [BLUEPRINT] MOD-INF-025 | docs/03_modules/_domain_infrastructure_operations/agent_to_agent_protocol/blueprint.md
# [MODULE] zephyr.infrastructure.a2a_protocol.layer3_coordination.a2a_saga
# [DOMAIN] D_INFRA_A2A
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_a2a_saga | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""A2A Saga 事务协议 — 多 Agent 跨步分布式事务

当跨 Agent 操作需要原子性保证时，使用 Saga 模式:
  每个 Agent 执行一步操作 + 提供补偿函数
  任一步失败 -> 逆序执行所有已完成步骤的补偿函数

对标: 微服务 Saga Orchestrator + 长期事务(Long Lived Transaction)
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

from dataclasses import dataclass, field
from enum import Enum


class SagaStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


@dataclass
class SagaStep:
    step_id: str
    agent_id: str
    action_name: str
    params: dict = field(default_factory=dict)
    result: dict = field(default_factory=dict)
    executed: bool = False
    compensate_called: bool = False


@dataclass
class SagaResult:
    saga_id: str
    status: SagaStatus
    steps: list[SagaStep] = field(default_factory=list)
    error_message: str = ""

    @property
    def executed_count(self) -> int:
        return sum(1 for s in self.steps if s.executed)

    @property
    def compensated_count(self) -> int:
        return sum(1 for s in self.steps if s.compensate_called)


class A2ASaga:
    """A2A Saga 事务协调器.

    执行模式: 顺序执行 -> 失败触发逆序补偿
    补偿注册: 每个 step 在 add_step 时声明其 compensate 策略
    """

    def __init__(self, saga_id: str):
        self._saga_id = saga_id
        self._steps: list[SagaStep] = []
        self._compensations: dict[str, dict] = {}
        self._status = SagaStatus.PENDING

    def add_step(
        self,
        step_id: str,
        agent_id: str,
        action_name: str,
        params: dict,
        compensate_action: str = "",
        compensate_params: dict | None = None,
    ) -> SagaStep:
        step = SagaStep(
            step_id=step_id,
            agent_id=agent_id,
            action_name=action_name,
            params=params,
        )
        self._steps.append(step)
        self._compensations[step_id] = {
            "action": compensate_action or f"compensate_{action_name}",
            "params": compensate_params or {},
        }
        return step

    def execute(
        self,
        action_funcs: dict[str, callable],
    ) -> SagaResult:
        self._status = SagaStatus.RUNNING
        result = SagaResult(saga_id=self._saga_id, status=SagaStatus.RUNNING)

        for step in self._steps:
            try:
                func = action_funcs.get(step.action_name, lambda p: {"ok": True})
                step.result = func(step.params)
                step.executed = True
            except Exception as e:
                result.status = SagaStatus.COMPENSATING
                result.error_message = "internal error"
                self._compensate(result, action_funcs)
                return result

        result.status = SagaStatus.COMPLETED
        result.steps = list(self._steps)
        self._status = SagaStatus.COMPLETED
        return result

    def _compensate(self, result: SagaResult, action_funcs: dict[str, callable]):
        for step in reversed(self._steps):
            if not step.executed:
                continue
            try:
                comp = self._compensations[step.step_id]
                func = action_funcs.get(comp["action"], lambda p: {"compensated": True})
                func(comp["params"])
                step.compensate_called = True
            except Exception as e:
                logger.warning("suppressed error in a2a_saga", exc_info=True)

        result.steps = list(self._steps)
        result.status = SagaStatus.COMPENSATED
        self._status = SagaStatus.COMPENSATED

    @property
    def status(self) -> SagaStatus:
        return self._status
