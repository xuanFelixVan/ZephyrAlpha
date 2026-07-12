# [A_test] module_id: SRC-TST-1370 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_phase_executor
# [INVARIANTS] PhaseExecutor enforces linear phase progression; cannot skip phases
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_phase_executor_root.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.execution.phase_executor import (
    PHASE_DEPENDENCIES,
    PHASE_LABELS,
    PHASE_ORDER,
    ConstructionPhase,
    ConstructionProgress,
    PhaseExecutor,
    PhaseState,
    PhaseStatus,
)


class TestConstructionPhase:
    def test_all_phases_defined(self):
        assert ConstructionPhase.PHASE_0.value == "phase_0"
        assert ConstructionPhase.PHASE_A.value == "phase_a"
        assert ConstructionPhase.PHASE_B.value == "phase_b"
        assert ConstructionPhase.PHASE_C.value == "phase_c"
        assert ConstructionPhase.PHASE_D.value == "phase_d"

    def test_phase_order_correct(self):
        assert PHASE_ORDER == (
            ConstructionPhase.PHASE_0,
            ConstructionPhase.PHASE_A,
            ConstructionPhase.PHASE_B,
            ConstructionPhase.PHASE_C,
            ConstructionPhase.PHASE_D,
        )


class TestPhaseDependencies:
    def test_phase_0_has_no_dependency(self):
        assert PHASE_DEPENDENCIES[ConstructionPhase.PHASE_0] is None

    def test_phase_a_depends_on_0(self):
        assert PHASE_DEPENDENCIES[ConstructionPhase.PHASE_A] == ConstructionPhase.PHASE_0

    def test_phase_b_depends_on_a(self):
        assert PHASE_DEPENDENCIES[ConstructionPhase.PHASE_B] == ConstructionPhase.PHASE_A

    def test_phase_c_depends_on_b(self):
        assert PHASE_DEPENDENCIES[ConstructionPhase.PHASE_C] == ConstructionPhase.PHASE_B

    def test_phase_d_depends_on_c(self):
        assert PHASE_DEPENDENCIES[ConstructionPhase.PHASE_D] == ConstructionPhase.PHASE_C


class TestPhaseLabels:
    def test_all_phases_have_labels(self):
        for phase in ConstructionPhase:
            assert phase in PHASE_LABELS
            assert len(PHASE_LABELS[phase]) > 0


class TestPhaseStatus:
    def test_values(self):
        assert PhaseStatus.NOT_STARTED.value == "not_started"
        assert PhaseStatus.IN_PROGRESS.value == "in_progress"
        assert PhaseStatus.COMPLETED.value == "completed"


class TestPhaseState:
    def test_defaults(self):
        ps = PhaseState(phase=ConstructionPhase.PHASE_0)
        assert ps.status == PhaseStatus.NOT_STARTED
        assert ps.started_at is None
        assert ps.completed_at is None
        assert ps.context_check_passed is False


class TestConstructionProgress:
    def test_defaults(self):
        p = ConstructionProgress()
        assert p.current_phase == ConstructionPhase.PHASE_0
        assert isinstance(p.phases, dict)


class TestPhaseExecutorInit:
    def test_initial_state(self):
        ex = PhaseExecutor()
        assert ex.current_phase == ConstructionPhase.PHASE_0
        for phase in ConstructionPhase:
            state = ex.get_phase_status(phase)
            assert state is not None
            assert state.status == PhaseStatus.NOT_STARTED


class TestPhaseExecutorCanStartPhase:
    def test_can_start_phase_0(self):
        ex = PhaseExecutor()
        can, reason = ex.can_start_phase(ConstructionPhase.PHASE_0)
        assert can is True
        assert reason == ""

    def test_cannot_start_phase_a_before_0_completed(self):
        ex = PhaseExecutor()
        can, reason = ex.can_start_phase(ConstructionPhase.PHASE_A)
        assert can is False
        assert "未完成" in reason

    def test_cannot_skip_phases(self):
        ex = PhaseExecutor()
        ex.start_phase(ConstructionPhase.PHASE_0)
        ex.complete_phase(ConstructionPhase.PHASE_0)
        can, reason = ex.can_start_phase(ConstructionPhase.PHASE_C)
        assert can is False


class TestPhaseExecutorStartPhase:
    def test_start_phase_0(self):
        ex = PhaseExecutor()
        result = ex.start_phase(ConstructionPhase.PHASE_0)
        assert result is True
        state = ex.get_phase_status(ConstructionPhase.PHASE_0)
        assert state.status == PhaseStatus.IN_PROGRESS
        assert state.started_at is not None
        assert state.context_check_passed is True

    def test_cannot_start_wrong_phase(self):
        ex = PhaseExecutor()
        result = ex.start_phase(ConstructionPhase.PHASE_A)
        assert result is False


class TestPhaseExecutorCompletePhase:
    def test_complete_phase_0(self):
        ex = PhaseExecutor()
        ex.start_phase(ConstructionPhase.PHASE_0)
        result = ex.complete_phase(ConstructionPhase.PHASE_0)
        assert result is True
        state = ex.get_phase_status(ConstructionPhase.PHASE_0)
        assert state.status == PhaseStatus.COMPLETED
        assert state.completed_at is not None

    def test_cannot_complete_not_started_phase(self):
        ex = PhaseExecutor()
        result = ex.complete_phase(ConstructionPhase.PHASE_0)
        assert result is False

    def test_complete_advances_current_phase(self):
        ex = PhaseExecutor()
        ex.start_phase(ConstructionPhase.PHASE_0)
        ex.complete_phase(ConstructionPhase.PHASE_0)
        assert ex.current_phase == ConstructionPhase.PHASE_A

    def test_full_progression(self):
        ex = PhaseExecutor()
        for phase in PHASE_ORDER:
            ex.start_phase(phase)
            ex.complete_phase(phase)
        assert ex.get_phase_status(ConstructionPhase.PHASE_D).status == PhaseStatus.COMPLETED


class TestPhaseExecutorRunContextCheck:
    def test_context_check_passes(self):
        ex = PhaseExecutor()
        result = ex.run_context_check()
        assert result is True
        state = ex.get_phase_status(ex.current_phase)
        assert state.context_check_passed is True


class TestPhaseExecutorGetPhaseStatus:
    def test_existing_phase(self):
        ex = PhaseExecutor()
        state = ex.get_phase_status(ConstructionPhase.PHASE_0)
        assert state is not None

    def test_nonexistent_phase_returns_none(self):
        ex = PhaseExecutor()
        ex._progress.phases.pop("phase_0", None)
        state = ex.get_phase_status(ConstructionPhase.PHASE_0)
        assert state is None


class TestPhaseExecutorProgress:
    def test_progress_property(self):
        ex = PhaseExecutor()
        p = ex.progress
        assert isinstance(p, ConstructionProgress)
        assert len(p.phases) == len(ConstructionPhase)
