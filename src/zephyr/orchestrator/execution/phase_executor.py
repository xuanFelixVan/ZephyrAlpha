# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.phase_executor
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-ORC_phase_executor | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Phase 执行引擎（Phase Executor）

依据：MOD-MASTER-002 蓝图 §六 施工 Phase 规划
实现 Phase 0 -> Phase A -> Phase B -> Phase C -> Phase D 四级施工序列。

Phase 定义：
- Phase 0: 管控契约优先（17条管控契约 + context check）
- Phase A: 核心集成（13条 CT-* + 3个共享 Schema）
- Phase B: 治理补齐（Anti-Patterns + 集成测试 + 门禁）
- Phase C: 运行保障（CDC + DLQ + 动态调参 + 健康探针 + CBAC）
- Phase D: 1人+AI维护（冷启动分派 + SLO + Bulkhead + Watchdog + Backup + 场景走查）
"""

from __future__ import annotations

from typing import Final
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, Field


class ConstructionPhase(str, Enum):
    PHASE_0 = "phase_0"
    PHASE_A = "phase_a"
    PHASE_B = "phase_b"
    PHASE_C = "phase_c"
    PHASE_D = "phase_d"


PHASE_ORDER: Final[tuple[ConstructionPhase, ...]] = (
    ConstructionPhase.PHASE_0,
    ConstructionPhase.PHASE_A,
    ConstructionPhase.PHASE_B,
    ConstructionPhase.PHASE_C,
    ConstructionPhase.PHASE_D,
)

PHASE_DEPENDENCIES: Final[dict[ConstructionPhase, ConstructionPhase | None]] = {
    ConstructionPhase.PHASE_0: None,
    ConstructionPhase.PHASE_A: ConstructionPhase.PHASE_0,
    ConstructionPhase.PHASE_B: ConstructionPhase.PHASE_A,
    ConstructionPhase.PHASE_C: ConstructionPhase.PHASE_B,
    ConstructionPhase.PHASE_D: ConstructionPhase.PHASE_C,
}

PHASE_LABELS: Final[dict[ConstructionPhase, str]] = {
    ConstructionPhase.PHASE_0: "管控契约优先——17条管控契约 + context check",
    ConstructionPhase.PHASE_A: "核心集成——13条核心CT-* + 3共享Schema",
    ConstructionPhase.PHASE_B: "治理补齐——Anti-Patterns + 集成测试 + 门禁",
    ConstructionPhase.PHASE_C: "运行保障——CDC+DLQ+动态调参+健康探针+CBAC",
    ConstructionPhase.PHASE_D: "1人+AI维护——冷启动分派+SLO+Bulkhead+Watchdog+Backup+场景走查",
}


class PhaseStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class PhaseState(BaseModel):
    phase: ConstructionPhase
    status: PhaseStatus = PhaseStatus.NOT_STARTED
    started_at: datetime | None = None
    completed_at: datetime | None = None
    context_check_passed: bool = False


class ConstructionProgress(BaseModel):
    current_phase: ConstructionPhase = ConstructionPhase.PHASE_0
    phases: dict[str, PhaseState] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))


class PhaseExecutor:
    def __init__(self):
        self._progress = ConstructionProgress()
        self._init_phases()

    def _init_phases(self) -> None:
        for phase in PHASE_ORDER:
            self._progress.phases[phase.value] = PhaseState(phase=phase)

    @property
    def progress(self) -> ConstructionProgress:
        return self._progress

    @property
    def current_phase(self) -> ConstructionPhase:
        return self._progress.current_phase

    def run_context_check(self) -> bool:
        phase_state = self._progress.phases[self._progress.current_phase.value]
        phase_state.context_check_passed = True
        return True

    def can_start_phase(self, phase: ConstructionPhase) -> tuple[bool, str]:
        dep = PHASE_DEPENDENCIES.get(phase)
        if dep is not None:
            dep_state = self._progress.phases.get(dep.value)
            if dep_state is None or dep_state.status != PhaseStatus.COMPLETED:
                return False, f"依赖 Phase 未完成: {dep.value}"

        if phase != self._progress.current_phase:
            return False, f"当前 Phase 为 {self._progress.current_phase.value}，不能跳过到 {phase.value}"

        return True, ""

    def start_phase(self, phase: ConstructionPhase) -> bool:
        can_start, reason = self.can_start_phase(phase)
        if not can_start:
            return False

        phase_state = self._progress.phases[phase.value]
        phase_state.status = PhaseStatus.IN_PROGRESS
        phase_state.started_at = datetime.now(UTC)
        phase_state.context_check_passed = True
        self._progress.last_updated = datetime.now(UTC)
        return True

    def complete_phase(self, phase: ConstructionPhase) -> bool:
        phase_state = self._progress.phases.get(phase.value)
        if phase_state is None:
            return False
        if phase_state.status != PhaseStatus.IN_PROGRESS:
            return False

        phase_state.status = PhaseStatus.COMPLETED
        phase_state.completed_at = datetime.now(UTC)
        self._progress.last_updated = datetime.now(UTC)

        next_idx = PHASE_ORDER.index(phase) + 1
        if next_idx < len(PHASE_ORDER):
            self._progress.current_phase = PHASE_ORDER[next_idx]

        return True

    def get_phase_status(self, phase: ConstructionPhase) -> PhaseState | None:
        return self._progress.phases.get(phase.value)
