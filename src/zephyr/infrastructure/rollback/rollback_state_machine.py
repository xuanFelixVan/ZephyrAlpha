# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] zephyr.infrastructure.rollback.rollback_state_machine
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-INF_rollback_state_machine | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""
RollbackStateMachine — 回滚步骤级状态机。

依据: 蓝图 MOD-INF-021 §6.10 B42, §7 Phase 5.2

六步骤回滚流水线:
    preflight → acquire_lock → git_revert → db_rebuild → verify → audit

每步状态: PENDING / SUCCESS / FAILED / RETRYING
可逆步: preflight, acquire_lock, db_rebuild, audit (可重试)
不可逆步: git_revert (失败→forward-fix commit)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class StepStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class StepType(str, Enum):
    REVERSIBLE = "reversible"
    IRREVERSIBLE = "irreversible"


@dataclass
class RollbackStep:
    name: str
    step_type: StepType
    status: StepStatus = StepStatus.PENDING
    retry_count: int = 0
    max_retries: int = 3
    started_at: str = ""
    completed_at: str = ""
    error: str = ""


@dataclass
class StateMachineResult:
    success: bool
    steps: list[RollbackStep]
    failed_step: str = ""
    overall_status: StepStatus = StepStatus.PENDING


class RollbackStateMachine:
    STEPS: list[tuple[str, StepType, int]] = [
        ("preflight", StepType.REVERSIBLE, 3),
        ("acquire_lock", StepType.REVERSIBLE, 5),
        ("git_revert", StepType.IRREVERSIBLE, 1),
        ("db_rebuild", StepType.REVERSIBLE, 3),
        ("verify", StepType.REVERSIBLE, 3),
        ("audit", StepType.REVERSIBLE, 3),
    ]

    def __init__(self, execution_id: str = "") -> None:
        self._execution_id = execution_id
        self._steps: list[RollbackStep] = []
        self._current_step_idx = 0
        self._init_steps()

    def _init_steps(self) -> None:
        self._steps = [RollbackStep(name=name, step_type=st, max_retries=retries) for name, st, retries in self.STEPS]

    @property
    def current_step(self) -> RollbackStep | None:
        if 0 <= self._current_step_idx < len(self._steps):
            return self._steps[self._current_step_idx]
        return None

    @property
    def steps(self) -> list[RollbackStep]:
        return self._steps

    def mark_current(self, status: StepStatus, error: str = "") -> None:
        step = self.current_step
        if not step:
            return

        step.status = status
        now = datetime.now(UTC).isoformat()
        if status == StepStatus.PENDING and not step.started_at:
            step.started_at = now

        if status in (StepStatus.SUCCESS, StepStatus.FAILED):
            step.completed_at = now
        if error:
            step.error = error

        if status == StepStatus.SUCCESS:
            self._current_step_idx += 1

    def retry_current(self) -> bool:
        step = self.current_step
        if not step:
            return False
        if step.retry_count >= step.max_retries:
            return False
        step.retry_count += 1
        step.status = StepStatus.RETRYING
        return True

    def is_current_reversible(self) -> bool:
        step = self.current_step
        return step.step_type is StepType.REVERSIBLE if step else True

    def is_complete(self) -> bool:
        return self._current_step_idx >= len(self._steps)

    def get_result(self) -> StateMachineResult:
        all_success = all(s.status == StepStatus.SUCCESS for s in self._steps)
        failed_steps = [s for s in self._steps if s.status == StepStatus.FAILED]
        failed_step = failed_steps[0].name if failed_steps else ""

        overall = StepStatus.SUCCESS if all_success else (StepStatus.FAILED if failed_steps else StepStatus.PENDING)

        return StateMachineResult(
            success=all_success,
            steps=self._steps,
            failed_step=failed_step,
            overall_status=overall,
        )

    def to_in_flight_data(self) -> dict[str, Any]:
        return {
            "execution_id": self._execution_id,
            "current_step_idx": self._current_step_idx,
            "steps": [
                {
                    "name": s.name,
                    "type": s.step_type.value,
                    "status": s.status.value,
                    "retry_count": s.retry_count,
                    "started_at": s.started_at,
                    "completed_at": s.completed_at,
                    "error": s.error,
                }
                for s in self._steps
            ],
        }

    @classmethod
    def from_in_flight_data(cls, data: dict[str, Any]) -> RollbackStateMachine:
        sm = cls(execution_id=data.get("execution_id", ""))
        sm._current_step_idx = data.get("current_step_idx", 0)
        steps_data = data.get("steps", [])
        for i, sd in enumerate(steps_data):
            if i < len(sm._steps):
                sm._steps[i].status = StepStatus(sd.get("status", "PENDING"))
                sm._steps[i].retry_count = sd.get("retry_count", 0)
                sm._steps[i].started_at = sd.get("started_at", "")
                sm._steps[i].completed_at = sd.get("completed_at", "")
                sm._steps[i].error = sd.get("error", "")
        return sm
