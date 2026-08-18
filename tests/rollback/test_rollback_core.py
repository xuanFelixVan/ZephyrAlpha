# [A_test] module_id: MOD-GOV_rollback_core | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-554 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.rollback.test_rollback_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: rollback_core (RollbackExecutor + KillSwitchManager)"""

import json
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.kill_switch import KillLevel, KillSwitchManager, KillSwitchStatus
from zephyr.infrastructure.rollback.rollback_executor import (
    DiscardDecision,
    PreflightResult,
    RollbackExecutor,
    RollbackOp,
)
from zephyr.infrastructure.rollback.rollback_lock import LockAcquireResult, RollbackLock


@pytest.fixture
def tmp_project(tmp_path):
    return tmp_path


@pytest.fixture
def kill_switch(tmp_project):
    return KillSwitchManager(project_root=tmp_project)


@pytest.fixture
def mock_dumper():
    dumper = MagicMock()
    dumper.restore.return_value = MagicMock(tables_restored=0, rows_restored=0)
    return dumper


@pytest.fixture
def mock_lock():
    lock = MagicMock(spec=RollbackLock)
    lock.acquire.return_value = LockAcquireResult(acquired=True, lock_id="RBLK-TEST", wait_time_ms=0)
    lock.release.return_value = LockAcquireResult(acquired=True, lock_id="RBLK-TEST", wait_time_ms=0)
    return lock


@pytest.fixture
def executor(tmp_project, mock_dumper, mock_lock):
    return RollbackExecutor(
        project_root=tmp_project,
        sqlite_dumper=mock_dumper,
        rollback_lock=mock_lock,
        owner_session_id="test-session-001",
    )


class TestRollbackExecutorInit:
    def test_default_instantiation(self, tmp_project):
        with (
            patch("zephyr.infrastructure.rollback.rollback_executor.SqliteDumper"),
            patch("zephyr.infrastructure.rollback.rollback_executor.RollbackLock"),
        ):
            ex = RollbackExecutor(project_root=tmp_project)
            assert ex.project_root == tmp_project
            assert ex.owner_session_id is None

    def test_custom_params(self, tmp_project, mock_dumper, mock_lock):
        ex = RollbackExecutor(
            project_root=tmp_project,
            sqlite_dumper=mock_dumper,
            rollback_lock=mock_lock,
            owner_session_id="session-abc",
        )
        assert ex.project_root == tmp_project
        assert ex.dumper is mock_dumper
        assert ex.lock is mock_lock
        assert ex.owner_session_id == "session-abc"

    def test_in_flight_dir_path(self, executor, tmp_project):
        expected = tmp_project / ".zephyr" / "rollback_in_flight"
        assert executor.in_flight_dir == expected


class TestExecutionId:
    def test_format(self, executor):
        eid = executor.generate_execution_id()
        assert eid.startswith("RBEXEC-")
        parts = eid.split("-")
        assert len(parts) >= 3

    def test_unique(self, executor):
        ids = {executor.generate_execution_id() for _ in range(20)}
        assert len(ids) == 20


class TestInFlightManagement:
    def test_write_and_read(self, executor):
        executor.write_in_flight("EID-001", "preflight", "PENDING")
        record = executor.read_in_flight("EID-001")
        assert record is not None
        assert record["execution_id"] == "EID-001"
        assert record["step"] == "preflight"
        assert record["status"] == "PENDING"

    def test_write_with_data(self, executor):
        executor.write_in_flight("EID-002", "git_revert", "SUCCESS", {"files_changed": 3})
        record = executor.read_in_flight("EID-002")
        assert record["data"]["files_changed"] == 3

    def test_read_nonexistent(self, executor):
        assert executor.read_in_flight("NO-SUCH-ID") is None

    def test_delete(self, executor):
        executor.write_in_flight("EID-003", "step", "PENDING")
        executor.delete_in_flight("EID-003")
        assert executor.read_in_flight("EID-003") is None

    def test_delete_nonexistent_no_error(self, executor):
        executor.delete_in_flight("NO-SUCH-ID")

    def test_get_in_flight_status(self, executor):
        executor.write_in_flight("EID-004", "step", "RUNNING")
        assert executor.get_in_flight_status("EID-004") == "RUNNING"

    def test_get_in_flight_status_missing(self, executor):
        assert executor.get_in_flight_status("MISSING") is None

    def test_recover_stale_in_flight(self, executor):
        executor.write_in_flight("EID-005", "git_revert", "FAILED", {"error": "boom"})
        recovered = executor.recover_stale_in_flight()
        assert "EID-005" in recovered
        record = executor.read_in_flight("EID-005")
        assert record["status"] == "RECOVERING"


class TestPreflightCheck:
    def test_clean_tree_passes(self, executor):
        executor.run_git = MagicMock(return_value="")
        result = executor.preflight_check()
        assert isinstance(result, PreflightResult)
        assert result.working_tree_clean is True
        assert result.not_detached_head is True

    def test_dirty_tree_fails(self, executor):
        def fake_git(args, **kwargs):
            if args == ["status", "--porcelain"]:
                return "M src/foo.py\n"
            if args == ["rev-parse", "--abbrev-ref", "HEAD"]:
                return "main"
            return ""

        executor.run_git = MagicMock(side_effect=fake_git)
        result = executor.preflight_check()
        assert result.passed is False
        assert result.working_tree_clean is False
        assert "Working tree is dirty" in result.errors

    def test_detached_head_fails(self, executor):
        def fake_git(args, **kwargs):
            if args == ["rev-parse", "--abbrev-ref", "HEAD"]:
                return "HEAD"
            return ""

        executor.run_git = MagicMock(side_effect=fake_git)
        result = executor.preflight_check()
        assert result.not_detached_head is False
        assert "Detached HEAD state" in result.errors


class TestPreview:
    def test_preview_returns_files(self, executor):
        def fake_git(args, **kwargs):
            if args[:2] == ["diff", "--name-only"]:
                return "src/a.py\nsrc/b.py\n"
            if args[:2] == ["diff", "--stat"]:
                return " 2 files changed, 10 insertions(+)\n"
            if args[:2] == ["log", "--oneline"]:
                return ""
            return ""

        executor.run_git = MagicMock(side_effect=fake_git)
        result = executor.preview("abc123")
        assert len(result.changed_files) == 2
        assert result.conflict_risk == "low"

    def test_preview_high_risk(self, executor):
        def fake_git(args, **kwargs):
            if args[:2] == ["diff", "--name-only"]:
                return "\n".join(f"src/f{i}.py" for i in range(15))
            if args[:2] == ["diff", "--stat"]:
                return "15 files\n"
            if args[:2] == ["log", "--oneline"]:
                return ""
            return ""

        executor.run_git = MagicMock(side_effect=fake_git)
        result = executor.preview("abc123")
        assert result.conflict_risk == "high"

    def test_preview_medium_risk(self, executor):
        def fake_git(args, **kwargs):
            if args[:2] == ["diff", "--name-only"]:
                return "\n".join(f"src/f{i}.py" for i in range(7))
            if args[:2] == ["diff", "--stat"]:
                return "7 files\n"
            if args[:2] == ["log", "--oneline"]:
                return ""
            return ""

        executor.run_git = MagicMock(side_effect=fake_git)
        result = executor.preview("abc123")
        assert result.conflict_risk == "medium"


class TestIsCommitted:
    def test_committed_file(self, executor):
        executor.run_git = MagicMock(return_value="src/a.py")
        result = executor.is_committed(["src/a.py"])
        assert result["src/a.py"] is True

    def test_uncommitted_file(self, executor):
        executor.run_git = MagicMock(side_effect=Exception("not tracked"))
        result = executor.is_committed(["src/missing.py"])
        assert result["src/missing.py"] is False


class TestDiscardChanges:
    def test_no_uncommitted_returns_no_changes(self, executor):
        executor.run_git = MagicMock(return_value="")
        executor.detect_owner_session_in_files = MagicMock(return_value=[])
        result = executor.discard_changes(["src/a.py"])
        assert result.decision == DiscardDecision.NO_CHANGES
        assert result.success is False

    def test_blocked_by_owner(self, executor):
        executor.detect_owner_session_in_files = MagicMock(return_value=["src/owned.py"])
        result = executor.discard_changes(["src/owned.py"])
        assert result.decision == DiscardDecision.BLOCKED_BY_OWNER
        assert result.success is False
        assert "src/owned.py" in result.files_blocked

    def test_force_discard_bypasses_owner(self, executor):
        def fake_git(args, **kwargs):
            if args == ["diff", "--name-only", "HEAD"]:
                return "src/a.py\n"
            if args == ["diff", "--cached", "--name-only"]:
                return ""
            if args[:2] == ["checkout", "--"]:
                return ""
            return ""

        executor.run_git = MagicMock(side_effect=fake_git)
        executor.detect_owner_session_in_files = MagicMock(return_value=["src/a.py"])
        executor.write_audit_log = MagicMock()
        result = executor.discard_changes(["src/a.py"], force=True)
        assert result.success is True
        assert result.decision == DiscardDecision.DISCARD


class TestHardReset:
    def test_requires_token(self, executor):
        with pytest.raises(ValueError, match="BREAK_GLASS token"):
            executor.hard_reset("abc123")


class TestForwardFixEvaluate:
    def test_low_risk_few_files(self, executor):
        executor.preview = MagicMock(return_value=MagicMock(conflict_risk="low", changed_files=["a.py", "b.py"]))
        assert executor.forward_fix_evaluate("abc123") is True

    def test_high_risk(self, executor):
        executor.preview = MagicMock(return_value=MagicMock(conflict_risk="high", changed_files=["a.py"]))
        assert executor.forward_fix_evaluate("abc123") is False

    def test_many_files(self, executor):
        executor.preview = MagicMock(return_value=MagicMock(conflict_risk="low", changed_files=["a", "b", "c", "d"]))
        assert executor.forward_fix_evaluate("abc123") is False


class TestDependencyImpactAnalysis:
    def test_impact_analysis(self, executor):
        def fake_git(args, **kwargs):
            if args[:2] == ["diff", "--name-only"]:
                return "src/zephyr/shared/utils.py\nsrc/zephyr/budget/main.py\nREADME.md\n"
            return ""

        executor.run_git = MagicMock(side_effect=fake_git)
        result = executor.dependency_impact_analysis("abc123")
        assert "shared" in result["impacted_modules"]
        assert "budget" in result["impacted_modules"]
        assert result["impact_breadth"] == 2

    def test_no_zephyr_files(self, executor):
        executor.run_git = MagicMock(return_value="README.md\nsetup.py\n")
        result = executor.dependency_impact_analysis("abc123")
        assert result["impact_breadth"] == 0


class TestCancelPendingRollback:
    def test_requires_token(self, executor):
        result = executor.cancel_pending_rollback("task-1", "reason")
        assert result["canceled"] is False

    def test_with_token_no_pending(self, executor):
        result = executor.cancel_pending_rollback("task-1", "reason", token="BREAK_GLASS")
        assert result["canceled"] is False

    def test_with_token_pending(self, executor):
        executor.write_in_flight("EID-CANCEL", "preflight", "PENDING")
        executor.write_op_audit = MagicMock()
        result = executor.cancel_pending_rollback("task-1", "reason", token="BREAK_GLASS")
        assert result["canceled"] is True


class TestBuildDiscardAudit:
    def test_audit_record_fields(self, executor):
        record = executor.build_discard_audit(
            decision=DiscardDecision.DISCARD,
            files=["a.py"],
            blocked=[],
            reason="test",
            audit_session="sess-1",
        )
        assert record["decision"] == "discard"
        assert record["files_in_scope"] == ["a.py"]
        assert record["session_id"] == "sess-1"
        assert "audit_id" in record
        assert "timestamp_utc" in record


class TestRollbackOpEnum:
    def test_all_values(self):
        assert RollbackOp.FULL_REVERT.value == "full_revert"
        assert RollbackOp.PARTIAL_REVERT.value == "partial_revert"
        assert RollbackOp.DISCARD.value == "discard"
        assert RollbackOp.HARD_RESET.value == "hard_reset"


class TestDiscardDecisionEnum:
    def test_all_values(self):
        assert DiscardDecision.DISCARD.value == "discard"
        assert DiscardDecision.REVERT.value == "revert"
        assert DiscardDecision.BLOCKED_BY_OWNER.value == "blocked_by_owner"
        assert DiscardDecision.NO_CHANGES.value == "no_changes"


class TestKillSwitchManagerInit:
    def test_default_path(self, tmp_project):
        ks = KillSwitchManager(project_root=tmp_project)
        assert ks.kill_path == tmp_project / ".zephyr" / "kill_switches.jsonl"


class TestKillSwitchActivate:
    def test_l1_session(self, kill_switch):
        entry = kill_switch.activate(KillLevel.L1_SESSION, "session-1", "test reason")
        assert entry.level == KillLevel.L1_SESSION
        assert entry.target == "session-1"
        assert entry.reason == "test reason"
        assert entry.activated_at != ""

    def test_l2_skill(self, kill_switch):
        entry = kill_switch.activate(KillLevel.L2_SKILL, "rollback", "skill issue")
        assert entry.level == KillLevel.L2_SKILL
        assert entry.target == "rollback"

    def test_l3_requires_token(self, kill_switch):
        with pytest.raises(ValueError, match="BREAK_GLASS token"):
            kill_switch.activate(KillLevel.L3_GLOBAL, "all", "emergency")

    def test_l3_with_token(self, kill_switch):
        entry = kill_switch.activate(KillLevel.L3_GLOBAL, "all", "emergency", token="BREAK_GLASS")
        assert entry.level == KillLevel.L3_GLOBAL
        assert entry.token_used == "BREAK_GLASS"

    def test_persists_to_file(self, kill_switch, tmp_project):
        kill_switch.activate(KillLevel.L1_SESSION, "sess-1", "reason")
        assert kill_switch.kill_path.exists()
        lines = kill_switch.kill_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["level"] == "L1_SESSION"


class TestKillSwitchDeactivate:
    def test_deactivate_existing(self, kill_switch):
        kill_switch.activate(KillLevel.L1_SESSION, "sess-1", "reason")
        result = kill_switch.deactivate(KillLevel.L1_SESSION, "sess-1")
        assert result is True
        status = kill_switch.status()
        assert "sess-1" not in status.sessions_killed

    def test_deactivate_nonexistent(self, kill_switch):
        result = kill_switch.deactivate(KillLevel.L1_SESSION, "no-such")
        assert result is False

    def test_deactivate_no_file(self, kill_switch):
        result = kill_switch.deactivate(KillLevel.L1_SESSION, "sess-1")
        assert result is False

    def test_deactivate_preserves_others(self, kill_switch):
        kill_switch.activate(KillLevel.L1_SESSION, "sess-1", "reason1")
        kill_switch.activate(KillLevel.L1_SESSION, "sess-2", "reason2")
        kill_switch.deactivate(KillLevel.L1_SESSION, "sess-1")
        status = kill_switch.status()
        assert "sess-2" in status.sessions_killed
        assert "sess-1" not in status.sessions_killed


class TestKillSwitchStatus:
    def test_empty_status(self, kill_switch):
        status = kill_switch.status()
        assert isinstance(status, KillSwitchStatus)
        assert status.global_killed is False
        assert status.sessions_killed == []
        assert status.skills_killed == []
        assert status.active_entries == 0

    def test_mixed_levels(self, kill_switch):
        kill_switch.activate(KillLevel.L1_SESSION, "sess-1", "r")
        kill_switch.activate(KillLevel.L2_SKILL, "rollback", "r")
        kill_switch.activate(KillLevel.L3_GLOBAL, "all", "r", token="TK")
        status = kill_switch.status()
        assert status.global_killed is True
        assert "sess-1" in status.sessions_killed
        assert "rollback" in status.skills_killed
        assert status.active_entries == 3


class TestKillSwitchIsKilled:
    def test_global_killed(self, kill_switch):
        kill_switch.activate(KillLevel.L3_GLOBAL, "all", "r", token="TK")
        killed, level = kill_switch.is_killed(session_id="sess-1")
        assert killed is True
        assert level == KillLevel.L3_GLOBAL

    def test_skill_killed(self, kill_switch):
        kill_switch.activate(KillLevel.L2_SKILL, "rollback", "r")
        killed, level = kill_switch.is_killed(skill_id="rollback")
        assert killed is True
        assert level == KillLevel.L2_SKILL

    def test_session_killed(self, kill_switch):
        kill_switch.activate(KillLevel.L1_SESSION, "sess-1", "r")
        killed, level = kill_switch.is_killed(session_id="sess-1")
        assert killed is True
        assert level == KillLevel.L1_SESSION

    def test_not_killed(self, kill_switch):
        killed, level = kill_switch.is_killed(session_id="sess-1")
        assert killed is False
        assert level == KillLevel.NONE

    def test_global_overrides_session(self, kill_switch):
        kill_switch.activate(KillLevel.L3_GLOBAL, "all", "r", token="TK")
        killed, level = kill_switch.is_killed(session_id="any", skill_id="any")
        assert killed is True
        assert level == KillLevel.L3_GLOBAL


class TestKillSwitchEscalate:
    def test_escalate_from_none_to_l1(self, kill_switch):
        entry = kill_switch.escalate("sess-1", "first issue")
        assert entry.level == KillLevel.L1_SESSION
        assert entry.target == "sess-1"

    def test_escalate_from_l1_to_l2(self, kill_switch):
        kill_switch.activate(KillLevel.L1_SESSION, "sess-1", "first")
        entry = kill_switch.escalate("sess-1", "escalating")
        assert entry.level == KillLevel.L2_SKILL
        assert "ESCALATED" in entry.reason
