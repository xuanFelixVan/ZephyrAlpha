# [A_test] module_id: MOD-GOV_phase_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_phase_manager
# [INVARIANTS] PHASE_SEQUENCE covers all ConstructionPhase values;phase_resolver returns lowest incomplete phase
# [MODIFY-GUARD] src/zephyr/rollback/phase_manager.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] GateResult.RED blocks phase transition;ValueError on invalid phase
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.governance.ops_governance.phase_manager import (
    PHASE_SEQUENCE,
    ConstructionPhase,
    GateResult,
    PhaseGate,
    get_next_phase,
    get_phase,
    phase_resolver,
)


class TestConstructionPhaseEnum:
    def test_enum_values(self):
        assert ConstructionPhase.PHASE_0_SKELETON.value == "PHASE_0_SKELETON"
        assert ConstructionPhase.PHASE_1_FUNCTIONAL.value == "PHASE_1_FUNCTIONAL"
        assert ConstructionPhase.PHASE_2_E2E.value == "PHASE_2_E2E"

    def test_enum_member_count(self):
        assert len(ConstructionPhase) == 3

    def test_enum_from_string(self):
        assert ConstructionPhase("PHASE_0_SKELETON") == ConstructionPhase.PHASE_0_SKELETON


class TestGateResultEnum:
    def test_enum_values(self):
        assert GateResult.GREEN.value == "GREEN"
        assert GateResult.YELLOW.value == "YELLOW"
        assert GateResult.RED.value == "RED"


class TestPhaseGateInstantiation:
    def test_basic_creation(self):
        gate = PhaseGate(
            phase=ConstructionPhase.PHASE_0_SKELETON,
            name="Test Gate",
            description="A test gate",
        )
        assert gate.phase == ConstructionPhase.PHASE_0_SKELETON
        assert gate.name == "Test Gate"
        assert gate.result == GateResult.GREEN

    def test_with_gate_checks(self):
        gate = PhaseGate(
            phase=ConstructionPhase.PHASE_0_SKELETON,
            name="Test",
            gate_checks=["check_a", "check_b", "check_c"],
        )
        assert gate.check_count == 3

    def test_empty_gate_checks(self):
        gate = PhaseGate(
            phase=ConstructionPhase.PHASE_0_SKELETON,
            name="Test",
        )
        assert gate.check_count == 0
        assert gate.gate_checks == []

    def test_with_dependencies(self):
        gate = PhaseGate(
            phase=ConstructionPhase.PHASE_1_FUNCTIONAL,
            name="Test",
            dependencies=[ConstructionPhase.PHASE_0_SKELETON],
        )
        assert ConstructionPhase.PHASE_0_SKELETON in gate.dependencies


class TestPhaseGateRunChecks:
    def test_all_green(self):
        gate = PhaseGate(
            phase=ConstructionPhase.PHASE_0_SKELETON,
            name="Test",
            gate_checks=["check1", "check2"],
        )
        mock_fn = MagicMock(return_value=GateResult.GREEN)
        result = gate.run_checks(check_fn=mock_fn)
        assert result == GateResult.GREEN
        assert gate.result == GateResult.GREEN

    def test_yellow_worst(self):
        gate = PhaseGate(
            phase=ConstructionPhase.PHASE_0_SKELETON,
            name="Test",
            gate_checks=["check1", "check2"],
        )

        def mock_check(name: str) -> GateResult:
            if name == "check1":
                return GateResult.GREEN
            return GateResult.YELLOW

        result = gate.run_checks(check_fn=mock_check)
        assert result == GateResult.YELLOW
        assert gate.result == GateResult.YELLOW

    def test_red_stops_early(self):
        gate = PhaseGate(
            phase=ConstructionPhase.PHASE_0_SKELETON,
            name="Test",
            gate_checks=["check1", "check2", "check3"],
        )
        call_count = 0

        def mock_check(name: str) -> GateResult:
            nonlocal call_count
            call_count += 1
            if name == "check1":
                return GateResult.RED
            return GateResult.GREEN

        result = gate.run_checks(check_fn=mock_check)
        assert result == GateResult.RED
        assert gate.result == GateResult.RED
        assert call_count == 1

    def test_empty_checks_returns_green(self):
        gate = PhaseGate(
            phase=ConstructionPhase.PHASE_0_SKELETON,
            name="Test",
            gate_checks=[],
        )
        mock_fn = MagicMock(return_value=GateResult.GREEN)
        result = gate.run_checks(check_fn=mock_fn)
        assert result == GateResult.GREEN
        mock_fn.assert_not_called()


class TestGetPhase:
    def test_valid_phase(self):
        gate = get_phase(ConstructionPhase.PHASE_0_SKELETON)
        assert gate is not None
        assert gate.phase == ConstructionPhase.PHASE_0_SKELETON

    def test_all_phases_present(self):
        for phase in ConstructionPhase:
            gate = get_phase(phase)
            assert gate is not None
            assert gate.phase == phase


class TestGetNextPhase:
    def test_phase0_next_is_phase1(self):
        assert get_next_phase(ConstructionPhase.PHASE_0_SKELETON) == ConstructionPhase.PHASE_1_FUNCTIONAL

    def test_phase1_next_is_phase2(self):
        assert get_next_phase(ConstructionPhase.PHASE_1_FUNCTIONAL) == ConstructionPhase.PHASE_2_E2E

    def test_phase2_has_no_next(self):
        assert get_next_phase(ConstructionPhase.PHASE_2_E2E) is None


class TestPhaseResolver:
    def test_empty_gates_returns_phase0(self):
        result = phase_resolver(set())
        assert result == ConstructionPhase.PHASE_0_SKELETON

    def test_partial_p0_returns_phase0(self):
        p0_gates = PHASE_SEQUENCE[ConstructionPhase.PHASE_0_SKELETON].gate_checks
        partial = set(p0_gates[:3])
        result = phase_resolver(partial)
        assert result == ConstructionPhase.PHASE_0_SKELETON

    def test_complete_p0_returns_phase0(self):
        p0_gates = set(PHASE_SEQUENCE[ConstructionPhase.PHASE_0_SKELETON].gate_checks)
        result = phase_resolver(p0_gates)
        assert result == ConstructionPhase.PHASE_0_SKELETON

    def test_complete_p0_and_p1_returns_phase1(self):
        p0_gates = set(PHASE_SEQUENCE[ConstructionPhase.PHASE_0_SKELETON].gate_checks)
        p1_gates = set(PHASE_SEQUENCE[ConstructionPhase.PHASE_1_FUNCTIONAL].gate_checks)
        result = phase_resolver(p0_gates | p1_gates)
        assert result == ConstructionPhase.PHASE_1_FUNCTIONAL

    def test_all_complete_returns_phase2(self):
        all_gates: set[str] = set()
        for phase in ConstructionPhase:
            all_gates |= set(PHASE_SEQUENCE[phase].gate_checks)
        result = phase_resolver(all_gates)
        assert result == ConstructionPhase.PHASE_2_E2E


class TestPhaseSequenceStructure:
    def test_all_phases_in_sequence(self):
        for phase in ConstructionPhase:
            assert phase in PHASE_SEQUENCE

    def test_phase0_has_no_dependencies(self):
        gate = PHASE_SEQUENCE[ConstructionPhase.PHASE_0_SKELETON]
        assert gate.dependencies == []

    def test_phase1_depends_on_phase0(self):
        gate = PHASE_SEQUENCE[ConstructionPhase.PHASE_1_FUNCTIONAL]
        assert ConstructionPhase.PHASE_0_SKELETON in gate.dependencies

    def test_phase2_depends_on_phase1(self):
        gate = PHASE_SEQUENCE[ConstructionPhase.PHASE_2_E2E]
        assert ConstructionPhase.PHASE_1_FUNCTIONAL in gate.dependencies

    def test_all_phases_have_gate_checks(self):
        for phase in ConstructionPhase:
            gate = PHASE_SEQUENCE[phase]
            assert len(gate.gate_checks) > 0, f"{phase.value} has no gate checks"

    def test_total_check_count(self):
        total = sum(len(PHASE_SEQUENCE[p].gate_checks) for p in ConstructionPhase)
        assert total >= 40, f"Expected >= 40 total checks, got {total}"
