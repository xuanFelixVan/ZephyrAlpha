# [A_test] module_id: MOD-GOV_task_lifecycle_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-437 | docs/03_modules/_cross_layer/shared_core/governance_core_blueprint.md | §
# [MODULE] tests.test_task_lifecycle_manager
# [INVARIANTS] TaskLifecycleManager is per-instance; no shared state
# [MODIFY-GUARD] task_lifecycle_manager.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no raises; returns (bool, str) tuples
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.infrastructure.lifecycle.task_lifecycle_manager import (
    GateID,
    GateResult,
    LifecycleState,
    TaskLifecycleManager,
    TaskStatus,
)


class TestTaskStatus:
    def test_values(self):
        assert TaskStatus.CREATED == "CREATED"
        assert TaskStatus.LOCKED == "LOCKED"
        assert TaskStatus.ASSIGNED == "ASSIGNED"
        assert TaskStatus.IN_PROGRESS == "IN_PROGRESS"
        assert TaskStatus.REVIEWING == "REVIEWING"
        assert TaskStatus.COMPLETED == "COMPLETED"
        assert TaskStatus.FAILED == "FAILED"


class TestGateID:
    def test_values(self):
        assert GateID.G0 == "G0_LOCK_VERIFICATION"
        assert GateID.G1 == "G1_CONTEXT_ASSEMBLY"
        assert GateID.G2 == "G2_BLUEPRINT_COMPLIANCE"
        assert GateID.G3 == "G3_CODE_GENERATION"
        assert GateID.G4 == "G4_VERIFICATION_TESTS"
        assert GateID.G5 == "G5_LINTING"
        assert GateID.G6 == "G6_ARTIFACT_COLLECTION"
        assert GateID.G7 == "G7_OUTPUT_COMPLETENESS"


class TestGateResult:
    def test_passed(self):
        result = GateResult(gate_id=GateID.G0, passed=True, details="ok")
        assert result.passed is True
        assert result.gate_id == GateID.G0
        assert result.timestamp_utc != ""

    def test_failed(self):
        result = GateResult(gate_id=GateID.G1, passed=False, details="missing context")
        assert result.passed is False
        assert result.details == "missing context"


class TestLifecycleState:
    def test_creation(self):
        state = LifecycleState(
            task_id="T1",
            status=TaskStatus.CREATED,
            completed_gates=[],
            blocked_gates={},
            transition_history=["init"],
            last_updated="2026-01-01T00:00:00Z",
        )
        assert state.task_id == "T1"
        assert state.status == TaskStatus.CREATED
        assert state.completed_gates == []
        assert state.blocked_gates == {}


class TestTaskLifecycleManagerInit:
    def test_default_root(self):
        mgr = TaskLifecycleManager()
        assert mgr.project_root == Path.cwd()

    def test_custom_root(self, tmp_path):
        mgr = TaskLifecycleManager(project_root=tmp_path)
        assert mgr.project_root == tmp_path


class TestTaskLifecycleManagerInitialize:
    def test_initialize_new_task(self):
        mgr = TaskLifecycleManager()
        state = mgr.initialize("T1")
        assert state.task_id == "T1"
        assert state.status == TaskStatus.CREATED
        assert state.completed_gates == []

    def test_initialize_existing_task(self):
        mgr = TaskLifecycleManager()
        s1 = mgr.initialize("T1")
        s2 = mgr.initialize("T1")
        assert s1 is s2

    def test_get_state(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        state = mgr.get_state("T1")
        assert state is not None
        assert state.task_id == "T1"

    def test_get_state_nonexistent(self):
        mgr = TaskLifecycleManager()
        assert mgr.get_state("nonexistent") is None


class TestTaskLifecycleManagerTransition:
    def test_valid_transition(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        ok, msg = mgr.transition("T1", TaskStatus.LOCKED)
        assert ok is True
        assert "succeeded" in msg
        assert mgr.get_state("T1").status == TaskStatus.LOCKED

    def test_invalid_transition(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        ok, msg = mgr.transition("T1", TaskStatus.COMPLETED)
        assert ok is False
        assert "Invalid" in msg
        assert mgr.get_state("T1").status == TaskStatus.CREATED

    def test_full_lifecycle(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        mgr.transition("T1", TaskStatus.LOCKED)
        mgr.transition("T1", TaskStatus.ASSIGNED)
        mgr.transition("T1", TaskStatus.IN_PROGRESS)
        mgr.transition("T1", TaskStatus.REVIEWING)
        ok, _ = mgr.transition("T1", TaskStatus.COMPLETED)
        assert ok is True
        assert mgr.get_state("T1").status == TaskStatus.COMPLETED

    def test_failed_from_created(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        ok, _ = mgr.transition("T1", TaskStatus.FAILED)
        assert ok is True
        assert mgr.get_state("T1").status == TaskStatus.FAILED

    def test_retry_from_failed(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        mgr.transition("T1", TaskStatus.FAILED)
        ok, _ = mgr.transition("T1", TaskStatus.CREATED)
        assert ok is True

    def test_completed_is_terminal(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        mgr.transition("T1", TaskStatus.LOCKED)
        mgr.transition("T1", TaskStatus.ASSIGNED)
        mgr.transition("T1", TaskStatus.IN_PROGRESS)
        mgr.transition("T1", TaskStatus.REVIEWING)
        mgr.transition("T1", TaskStatus.COMPLETED)
        ok, _ = mgr.transition("T1", TaskStatus.CREATED)
        assert ok is False

    def test_transition_history_recorded(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        mgr.transition("T1", TaskStatus.LOCKED)
        state = mgr.get_state("T1")
        assert len(state.transition_history) >= 2
        assert any("CREATED" in h and "LOCKED" in h for h in state.transition_history)


class TestTaskLifecycleManagerPassGate:
    def test_pass_gate(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        result = mgr.pass_gate("T1", GateID.G0, "lock verified")
        assert result.passed is True
        assert result.gate_id == GateID.G0
        state = mgr.get_state("T1")
        assert GateID.G0 in state.completed_gates

    def test_pass_gate_idempotent(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        mgr.pass_gate("T1", GateID.G0, "ok")
        mgr.pass_gate("T1", GateID.G0, "ok again")
        state = mgr.get_state("T1")
        assert state.completed_gates.count(GateID.G0) == 1

    def test_pass_gate_removes_block(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        mgr.block_gate("T1", GateID.G0, "blocked")
        assert GateID.G0 in mgr.get_state("T1").blocked_gates
        mgr.pass_gate("T1", GateID.G0, "fixed")
        assert GateID.G0 not in mgr.get_state("T1").blocked_gates


class TestTaskLifecycleManagerBlockGate:
    def test_block_gate(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        result = mgr.block_gate("T1", GateID.G1, "missing context")
        assert result.passed is False
        assert result.details == "missing context"
        state = mgr.get_state("T1")
        assert GateID.G1 in state.blocked_gates
        assert state.blocked_gates[GateID.G1] == "missing context"


class TestTaskLifecycleManagerAllGatesPassed:
    def test_no_gates_passed(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        assert mgr.all_gates_passed("T1") is False

    def test_some_gates_passed(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        mgr.pass_gate("T1", GateID.G0, "ok")
        assert mgr.all_gates_passed("T1") is False

    def test_all_gates_passed(self):
        mgr = TaskLifecycleManager()
        mgr.initialize("T1")
        for gate in GateID:
            mgr.pass_gate("T1", gate, "ok")
        assert mgr.all_gates_passed("T1") is True

    def test_nonexistent_task(self):
        mgr = TaskLifecycleManager()
        assert mgr.all_gates_passed("nonexistent") is False


class TestTaskLifecycleManagerGateG7Output:
    def test_empty_downstream_outputs(self):
        mgr = TaskLifecycleManager()
        card = {"downstream_outputs": [], "rollback_instructions": "undo"}
        result = mgr.gate_g7_output(card)
        assert result.passed is False
        assert "downstream_outputs is empty" in result.details

    def test_missing_path_in_output(self):
        mgr = TaskLifecycleManager()
        card = {
            "downstream_outputs": [{"not_path": "x"}],
            "rollback_instructions": "undo",
        }
        result = mgr.gate_g7_output(card)
        assert result.passed is False
        assert "missing 'path'" in result.details

    def test_output_path_not_found(self, tmp_path):
        mgr = TaskLifecycleManager(project_root=tmp_path)
        card = {
            "downstream_outputs": [{"path": "nonexistent.py"}],
            "rollback_instructions": "undo",
        }
        result = mgr.gate_g7_output(card)
        assert result.passed is False
        assert "not found" in result.details

    def test_empty_rollback_instructions(self, tmp_path):
        (tmp_path / "out.py").write_text("x = 1", encoding="utf-8")
        mgr = TaskLifecycleManager(project_root=tmp_path)
        card = {
            "downstream_outputs": [{"path": "out.py"}],
            "rollback_instructions": "",
        }
        result = mgr.gate_g7_output(card)
        assert result.passed is False
        assert "rollback_instructions is empty" in result.details

    def test_manifest_path_not_found(self, tmp_path):
        (tmp_path / "out.py").write_text("x = 1", encoding="utf-8")
        mgr = TaskLifecycleManager(project_root=tmp_path)
        card = {
            "downstream_outputs": [{"path": "out.py"}],
            "rollback_instructions": "undo",
            "context_assembly_manifest": [{"file_path": "missing.py"}],
        }
        result = mgr.gate_g7_output(card)
        assert result.passed is False
        assert "context_assembly_manifest" in result.details

    def test_all_valid(self, tmp_path):
        (tmp_path / "out.py").write_text("x = 1", encoding="utf-8")
        (tmp_path / "ctx.py").write_text("y = 2", encoding="utf-8")
        mgr = TaskLifecycleManager(project_root=tmp_path)
        card = {
            "downstream_outputs": [{"path": "out.py"}],
            "rollback_instructions": "undo all changes",
            "context_assembly_manifest": [{"file_path": "ctx.py"}],
        }
        result = mgr.gate_g7_output(card)
        assert result.passed is True
        assert "G7 PASSED" in result.details

    def test_no_card_fields(self):
        mgr = TaskLifecycleManager()
        result = mgr.gate_g7_output({})
        assert result.passed is False

    def test_manifest_with_empty_file_path(self, tmp_path):
        (tmp_path / "out.py").write_text("x = 1", encoding="utf-8")
        mgr = TaskLifecycleManager(project_root=tmp_path)
        card = {
            "downstream_outputs": [{"path": "out.py"}],
            "rollback_instructions": "undo",
            "context_assembly_manifest": [{"file_path": ""}],
        }
        result = mgr.gate_g7_output(card)
        assert result.passed is True
