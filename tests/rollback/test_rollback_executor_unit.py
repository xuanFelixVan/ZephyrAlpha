# [A_test] module_id: SRC-TST-2059 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-676 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_rollback_executor
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for RollbackExecutor — rollback core executor (MOD-INF-021 §7).

Tests: preflight_check, preview, discard_changes, full_revert,
partial_revert, hard_reset, forward_fix_evaluate, cancel_pending_rollback,
dependency_impact_analysis, in_flight lifecycle.
"""


import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from zephyr.infrastructure.rollback.rollback_executor import (
    DiscardDecision,
    DiscardResult,
    PreviewResult,
    RollbackExecutor,
    RollbackOp,
    RollbackExecutionResult,
)


class TestPreflightCheck:
    """preflight_check() — Git 状态七维安全预检"""

    def test_all_clean(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.side_effect = [
                "",
                "main",
                "abc123",
                "abc123",
            ]
            result = exec.preflight_check()
            assert result.passed
            assert result.working_tree_clean
            assert len(result.errors) == 0

    def test_dirty_working_tree(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.side_effect = [
                " M file.py",
                "main",
                "abc123",
                "abc123",
            ]
            result = exec.preflight_check()
            assert not result.passed
            assert "Working tree is dirty" in result.errors

    def test_detached_head(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.side_effect = [
                "",
                "HEAD",
                "abc123",
                "abc123",
            ]
            result = exec.preflight_check()
            assert not result.passed
            assert not result.not_detached_head
            assert "Detached HEAD state" in result.errors


class TestPreview:
    """preview() — 回滚前变更预览"""

    def test_preview_low_risk(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.side_effect = [
                "src/a.py\nsrc/b.py",
                " 2 files changed | 50 ++",
                "",
            ]
            result = exec.preview("abc123")
            assert result.conflict_risk == "low"
            assert len(result.changed_files) == 2

    def test_preview_medium_risk(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.side_effect = [
                "\n".join(f"src/f{i}.py" for i in range(8)),
                " 8 files changed",
                "",
            ]
            result = exec.preview("abc123")
            assert result.conflict_risk == "medium"

    def test_preview_high_risk(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.side_effect = [
                "\n".join(f"src/f{i}.py" for i in range(15)),
                " 15 files changed",
                "abc Merge",
            ]
            result = exec.preview("abc123")
            assert result.conflict_risk == "high"

    def test_preview_merge_detected_high_risk(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.side_effect = [
                "src/a.py",
                " 1 file changed",
                "abc123 Merge branch 'feature'",
            ]
            result = exec.preview("abc123")
            assert result.conflict_risk == "high"


class TestDiscardChanges:
    """discard_changes() — 丢弃未提交变更的三路由调度"""

    def test_discard_uncommitted_files(self):
        exec = RollbackExecutor()
        with (
            patch.object(exec, "_run_git") as mock_git,
            patch.object(exec, "_detect_owner_session_in_files", return_value=[]),
            patch.object(exec, "get_uncommitted_files", return_value=["file.py"]),
            patch.object(exec, "get_staged_uncommitted_files", return_value=[]),
            patch.object(exec, "_write_audit_log"),
        ):
            mock_git.return_value = ""
            result = exec.discard_changes(["file.py"])
            assert result.success
            assert result.decision == DiscardDecision.DISCARD
            assert "file.py" in result.files_discarded

    def test_discard_blocked_by_owner(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_detect_owner_session_in_files", return_value=["file.py"]):
            result = exec.discard_changes(["file.py"], force=False)
            assert not result.success
            assert result.decision == DiscardDecision.BLOCKED_BY_OWNER
            assert "file.py" in result.files_blocked

    def test_discard_force_bypasses_owner(self):
        exec = RollbackExecutor()
        with (
            patch.object(exec, "_detect_owner_session_in_files", return_value=[]),
            patch.object(exec, "get_uncommitted_files", return_value=["file.py"]),
            patch.object(exec, "get_staged_uncommitted_files", return_value=[]),
            patch.object(exec, "_run_git") as mock_git,
            patch.object(exec, "_write_audit_log"),
        ):
            mock_git.return_value = ""
            result = exec.discard_changes(["file.py"], force=True)
            assert result.success

    def test_discard_no_changes(self):
        exec = RollbackExecutor()
        with (
            patch.object(exec, "_detect_owner_session_in_files", return_value=[]),
            patch.object(exec, "get_uncommitted_files", return_value=[]),
            patch.object(exec, "get_staged_uncommitted_files", return_value=[]),
        ):
            result = exec.discard_changes(["file.py"])
            assert not result.success
            assert result.decision == DiscardDecision.NO_CHANGES


class TestRollbackOrDiscard:
    """rollback_or_discard() — 混合回滚/丢弃路由"""

    def test_all_uncommitted_routes_to_discard(self):
        exec = RollbackExecutor()
        with (
            patch.object(exec, "is_committed", return_value={"file.py": False}),
            patch.object(exec, "discard_changes") as mock_discard,
        ):
            mock_discard.return_value = DiscardResult(
                success=True,
                files_discarded=["file.py"],
                files_blocked=[],
                decision=DiscardDecision.DISCARD,
                audit_record={},
            )
            result = exec.rollback_or_discard(["file.py"])
            assert result.decision == DiscardDecision.DISCARD
            mock_discard.assert_called_once()

    def test_all_committed_routes_to_revert(self):
        exec = RollbackExecutor()
        with (
            patch.object(exec, "is_committed", return_value={"file.py": True}),
            patch.object(exec, "_run_git", return_value="abc1234"),
            patch.object(exec, "full_revert") as mock_revert,
            patch.object(exec, "_write_audit_log"),
        ):
            mock_revert.return_value = RollbackExecutionResult(
                success=True,
                operation=RollbackOp.FULL_REVERT,
                commit_sha="abc123",
                files_reverted=1,
                db_tables_restored=0,
                db_rows_restored=0,
            )
            result = exec.rollback_or_discard(["file.py"], commit_sha="abc123")
            assert result.decision == DiscardDecision.REVERT


class TestHardReset:
    """hard_reset() — BREAK_GLASS 硬重置"""

    def test_hard_reset_requires_token(self):
        exec = RollbackExecutor()
        with pytest.raises(ValueError, match="BREAK_GLASS token"):
            exec.hard_reset("abc123")

    def test_hard_reset_with_token(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_lsg_verify_critical_operation"), patch.object(exec, "_execute") as mock_exec:
            mock_exec.return_value = RollbackExecutionResult(
                success=True,
                operation=RollbackOp.HARD_RESET,
                commit_sha="abc123",
                files_reverted=0,
                db_tables_restored=0,
                db_rows_restored=0,
            )
            result = exec.hard_reset("abc123", token="BREAK_GLASS_TOKEN")
            assert result.success
            assert result.operation == RollbackOp.HARD_RESET


class TestForwardFixEvaluate:
    """forward_fix_evaluate() — 评估是否适合 forward-fix 替代回滚"""

    def test_forward_fix_low_risk_eligible(self):
        exec = RollbackExecutor()
        with patch.object(exec, "preview") as mock_preview:
            mock_preview.return_value = PreviewResult(
                changed_files=["src/a.py"],
                conflict_risk="low",
            )
            assert exec.forward_fix_evaluate("abc123")

    def test_forward_fix_high_risk_ineligible(self):
        exec = RollbackExecutor()
        with patch.object(exec, "preview") as mock_preview:
            mock_preview.return_value = PreviewResult(
                changed_files=["src/a.py"],
                conflict_risk="high",
            )
            assert not exec.forward_fix_evaluate("abc123")

    def test_forward_fix_too_many_files(self):
        exec = RollbackExecutor()
        with patch.object(exec, "preview") as mock_preview:
            mock_preview.return_value = PreviewResult(
                changed_files=["f1.py", "f2.py", "f3.py", "f4.py"],
                conflict_risk="low",
            )
            assert not exec.forward_fix_evaluate("abc123")


class TestDependencyImpactAnalysis:
    """dependency_impact_analysis() — 跨模块影响分析"""

    def test_identifies_impacted_modules(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.return_value = "src/zephyr/rollback/executor.py\nsrc/zephyr/gov_enforcement/rule_enforcement/_registry.yaml"
            result = exec.dependency_impact_analysis("abc123")
            modules = result.get("impacted_modules", [])
            assert len(modules) > 0


class TestCancelPendingRollback:
    """cancel_pending_rollback() — BREAK_GLASS 取消待执行回滚"""

    def test_cancel_requires_token(self):
        exec = RollbackExecutor()
        result = exec.cancel_pending_rollback("TASK-001", "test")
        assert not result["canceled"]
        assert "BREAK_GLASS" in result["reason"]


class TestDiscardConcurrencyGuard:
    """discard_changes() 并发安全守卫 — .ailocks 锁冲突检测（方案C）"""

    def test_discard_blocked_by_other_session_lock(self):
        """文件被其他 session 锁定 → BLOCKED_BY_OWNER"""
        from zephyr.infrastructure.runtime.concurrency_guard import ConflictResult

        exec = RollbackExecutor()
        conflict = ConflictResult(
            has_conflict=True,
            blocked_files=["file.py"],
            locked_by={"file.py": "session-OTHER"},
            reason="locked",
        )
        with (
            patch.object(exec, "_detect_owner_session_in_files", return_value=[]),
            patch("zephyr.infrastructure.rollback.rollback_executor.check_rollback_conflict", return_value=conflict),
        ):
            result = exec.discard_changes(["file.py"], force=False)
            assert not result.success
            assert result.decision == DiscardDecision.BLOCKED_BY_OWNER
            assert "file.py" in result.files_blocked

    def test_discard_no_lock_conflict_proceeds(self):
        """无锁冲突 → 正常进入 discard 流程"""
        from zephyr.infrastructure.runtime.concurrency_guard import ConflictResult

        exec = RollbackExecutor()
        conflict = ConflictResult(has_conflict=False, blocked_files=[])
        with (
            patch.object(exec, "_detect_owner_session_in_files", return_value=[]),
            patch("zephyr.infrastructure.rollback.rollback_executor.check_rollback_conflict", return_value=conflict),
            patch.object(exec, "get_uncommitted_files", return_value=["file.py"]),
            patch.object(exec, "get_staged_uncommitted_files", return_value=[]),
            patch.object(exec, "_run_git", return_value=""),
            patch.object(exec, "_write_audit_log"),
        ):
            result = exec.discard_changes(["file.py"], force=False)
            assert result.success
            assert result.decision == DiscardDecision.DISCARD


class TestExecuteConcurrencyGuard:
    """_execute() 并发安全守卫 — 前置冲突检测 + stash 安全化（方案C）"""

    def test_execute_blocked_by_concurrency_conflict(self):
        """回滚文件被其他 session 锁定 → 返回失败"""
        from zephyr.infrastructure.runtime.concurrency_guard import ConflictResult

        exec = RollbackExecutor()
        conflict = ConflictResult(
            has_conflict=True,
            blocked_files=["src/a.py"],
            locked_by={"src/a.py": "session-OTHER"},
            reason="locked",
        )
        with (
            patch.object(exec, "_resolve_conflict_files", return_value=["src/a.py"]),
            patch("zephyr.infrastructure.rollback.rollback_executor.check_rollback_conflict", return_value=conflict),
            patch.object(exec, "_write_in_flight"),
            patch.object(exec, "_write_op_audit"),
        ):
            result = exec._execute(
                operation=RollbackOp.FULL_REVERT,
                commit_sha="abc123",
                audit_session="test",
            )
            assert not result.success
            assert "concurrency conflict" in result.errors[0].lower()

    def test_execute_stash_blocked_other_session_files(self):
        """stash 前发现其他 session 未提交文件 → 阻断"""
        from zephyr.infrastructure.rollback.rollback_executor import PreflightResult
        from zephyr.infrastructure.runtime.concurrency_guard import StashPlan

        exec = RollbackExecutor()
        preflight = PreflightResult(
            passed=False,
            working_tree_clean=False,
            not_detached_head=True,
            remote_not_ahead=True,
            not_in_rebase=True,
            not_in_merge=True,
            errors=["Working tree is dirty"],
        )
        stash_plan = StashPlan(
            should_stash=True,
            own_files=["own.py"],
            other_files=["other.py"],
            other_owners={"other.py": "session-OTHER"},
        )
        with (
            patch.object(exec, "_resolve_conflict_files", return_value=[]),
            patch.object(exec, "preflight_check", return_value=preflight),
            patch.object(exec, "get_uncommitted_files", return_value=["own.py"]),
            patch.object(exec, "get_staged_uncommitted_files", return_value=["other.py"]),
            patch("zephyr.infrastructure.rollback.rollback_executor.classify_uncommitted_files", return_value=stash_plan),
            patch.object(exec, "_write_in_flight"),
            patch.object(exec, "_write_op_audit"),
        ):
            result = exec._execute(
                operation=RollbackOp.FULL_REVERT,
                commit_sha="abc123",
                audit_session="test",
            )
            assert not result.success
            assert "blocked stash" in result.errors[0].lower()


class TestInFlightLifecycle:
    """_write_in_flight / _read_in_flight / _delete_in_flight — 飞行记录"""

    def test_in_flight_create_read_delete(self):
        exec = RollbackExecutor(project_root=Path(tempfile.mkdtemp()))
        eid = "RBEXEC-test-001"
        exec._write_in_flight(eid, "test_step", "PENDING")
        record = exec._read_in_flight(eid)
        assert record is not None
        assert record["step"] == "test_step"
        assert record["status"] == "PENDING"
        exec._delete_in_flight(eid)
        assert exec._read_in_flight(eid) is None

    def test_recover_stale_in_flight(self):
        exec = RollbackExecutor(project_root=Path(tempfile.mkdtemp()))
        eid = "RBEXEC-stale-001"
        exec._write_in_flight(eid, "stale_step", "FAILED")
        recovered = exec._recover_stale_in_flight()
        assert len(recovered) > 0
        record = exec._read_in_flight(eid)
        assert record["status"] == "RECOVERING"
        exec._delete_in_flight(eid)


class TestIsCommitted:
    """is_committed() / get_uncommitted_files() — 提交状态检查"""

    def test_tracked_file(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.return_value = ""
            result = exec.is_committed(["tracked.py"])
            assert result["tracked.py"]

    def test_untracked_file(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.side_effect = Exception("not tracked")
            result = exec.is_committed(["untracked.py"])
            assert not result["untracked.py"]

    def test_get_uncommitted_files(self):
        exec = RollbackExecutor()
        with patch.object(exec, "_run_git") as mock_git:
            mock_git.return_value = "src/a.py\nconfig/b.yaml"
            result = exec.get_uncommitted_files()
            assert len(result) == 2
            assert "src/a.py" in result
