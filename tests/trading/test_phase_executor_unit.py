# [A_test] module_id: SRC-TST-2051 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-668 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_phase_executor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""Phase 执行引擎单元测试——验证 Phase 0→D 四级施工序列。"""


import pytest

from zephyr.orchestrator.execution.phase_executor import (
    PHASE_DEPENDENCIES,
    PHASE_ORDER,
    ConstructionPhase,
    PhaseExecutor,
    PhaseStatus,
)


@pytest.fixture
def executor():
    return PhaseExecutor()


class TestPhaseOrder:
    def test_five_phases_defined(self):
        assert len(PHASE_ORDER) == 5

    def test_phase_0_first(self):
        assert PHASE_ORDER[0] == ConstructionPhase.PHASE_0

    def test_phase_d_last(self):
        assert PHASE_ORDER[-1] == ConstructionPhase.PHASE_D

    def test_all_dependencies_defined(self):
        for phase in PHASE_ORDER:
            assert phase in PHASE_DEPENDENCIES


class TestInitialState:
    def test_current_phase_is_phase_0(self, executor):
        assert executor.current_phase == ConstructionPhase.PHASE_0

    def test_all_phases_not_started(self, executor):
        for phase in PHASE_ORDER:
            state = executor.get_phase_status(phase)
            assert state is not None
            assert state.status == PhaseStatus.NOT_STARTED


class TestContextCheck:
    def test_context_check_passes(self, executor):
        assert executor.run_context_check()
        state = executor.get_phase_status(ConstructionPhase.PHASE_0)
        assert state.context_check_passed is True


class TestCanStartPhase:
    def test_can_start_phase_0(self, executor):
        allowed, _ = executor.can_start_phase(ConstructionPhase.PHASE_0)
        assert allowed

    def test_cannot_skip_phase(self, executor):
        allowed, reason = executor.can_start_phase(ConstructionPhase.PHASE_B)
        assert not allowed
        assert "不能跳过" in reason


class TestStartComplete:
    def test_start_phase_0(self, executor):
        assert executor.start_phase(ConstructionPhase.PHASE_0)
        state = executor.get_phase_status(ConstructionPhase.PHASE_0)
        assert state.status == PhaseStatus.IN_PROGRESS

    def test_complete_phase_0_advances_to_a(self, executor):
        executor.start_phase(ConstructionPhase.PHASE_0)
        assert executor.complete_phase(ConstructionPhase.PHASE_0)
        assert executor.current_phase == ConstructionPhase.PHASE_A
        state = executor.get_phase_status(ConstructionPhase.PHASE_0)
        assert state.status == PhaseStatus.COMPLETED

    def test_cannot_complete_not_started(self, executor):
        assert not executor.complete_phase(ConstructionPhase.PHASE_0)

    def test_full_pipeline(self, executor):
        for phase in PHASE_ORDER:
            assert executor.start_phase(phase)
            assert executor.complete_phase(phase)
        assert executor.current_phase == ConstructionPhase.PHASE_D
        for phase in PHASE_ORDER:
            state = executor.get_phase_status(phase)
            assert state.status == PhaseStatus.COMPLETED


class TestDependencyCheck:
    def test_phase_a_depends_on_phase_0(self, executor):
        allowed, _ = executor.can_start_phase(ConstructionPhase.PHASE_A)
        assert not allowed
        assert "依赖 Phase 未完成" in _
