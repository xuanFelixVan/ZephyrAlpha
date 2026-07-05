# [BLUEPRINT] SRC-088 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.compensation.saga_compensator
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_saga_compensator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Saga Compensator — 补偿事务：多步操作任一失败 → 反向补偿。

依据：
    蓝图 MOD-TASK_SYSTEM §6.8 + v0.6.0
    任务卡 TASK-INF-0113
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class SagaStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"


@dataclass
class SagaStep:
    step_id: str
    action: Callable
    compensation: Callable
    executed: bool = False
    compensated: bool = False
    error: str = ""


@dataclass
class SagaContext:
    saga_id: str
    steps: list[SagaStep]
    status: SagaStatus = SagaStatus.PENDING
    current_step: int = 0
    errors: list[str] = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class SagaCompensator:
    def __init__(self) -> None:
        self._sagas: dict[str, SagaContext] = {}

    def create_saga(self, saga_id: str, steps: list[SagaStep]) -> SagaContext:
        context = SagaContext(saga_id=saga_id, steps=steps)
        self._sagas[saga_id] = context
        return context

    def execute(self, saga_id: str) -> tuple[bool, SagaContext]:
        context = self._sagas.get(saga_id)

        if context is None:
            return False, SagaContext(saga_id="NOT_FOUND", steps=[])

        context.status = SagaStatus.RUNNING

        for i, step in enumerate(context.steps):
            context.current_step = i
            try:
                step.action()
                step.executed = True
            except Exception as e:
                context.errors.append(f"Step {step.step_id} failed: {e}")
                self._compensate(context, i)
                return False, context

        context.status = SagaStatus.COMPLETED
        return True, context

    def compensate_all(self, saga_id: str) -> tuple[bool, SagaContext]:
        context = self._sagas.get(saga_id)

        if context is None:
            return False, SagaContext(saga_id="NOT_FOUND", steps=[])

        self._compensate(context, len(context.steps) - 1)

        return len(context.errors) == 0, context

    def get_status(self, saga_id: str) -> SagaContext | None:
        return self._sagas.get(saga_id)

    def _compensate(self, context: SagaContext, failed_index: int) -> None:
        context.status = SagaStatus.COMPENSATING

        for i in range(failed_index, -1, -1):
            step = context.steps[i]
            if step.executed and not step.compensated:
                try:
                    step.compensation()
                    step.compensated = True
                except Exception as e:
                    context.errors.append(f"Compensation for {step.step_id} failed: {e}")

        if context.errors:
            context.status = SagaStatus.FAILED
        else:
            context.status = SagaStatus.COMPLETED
