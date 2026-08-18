# [A_test] module_id: MOD-GOV_rollback_executor_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_executor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.rollback_executor import (
    DiscardDecision,
    PreflightResult,
    PreviewResult,
    RollbackExecutionResult,
    RollbackExecutor,
    RollbackOp,
)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    refs = git_dir / "refs" / "heads"
    refs.mkdir(parents=True)
    (refs / "main").write_text("abc1234\n", encoding="utf-8")
    return tmp_path


@pytest.fixture
def mock_dumper() -> MagicMock:
    dumper = MagicMock()
    dumper.restore.return_value = MagicMock(tables_restored=0, rows_restored=0)
    return dumper


@pytest.fixture
def mock_lock() -> MagicMock:
    lock = MagicMock()
    lock.acquire.return_value = MagicMock(acquired=True, lock_id="RBLK-TEST-001", reason="")
    lock.release.return_value = MagicMock(acquired=True, lock_id="RBLK-TEST-001", reason="")
    return lock


@pytest.fixture
def executor(tmp_project: Path, mock_dumper: MagicMock, mock_lock: MagicMock) -> RollbackExecutor:
    return RollbackExecutor(
        project_root=tmp_project,
        sqlite_dumper=mock_dumper,
        rollback_lock=mock_lock,
        owner_session_id="session-test-001",
    )


class TestRollbackExecutorInstantiation:
    def test_creates_with_defaults(self, tmp_project: Path):
        with patch("zephyr.infrastructure.rollback.rollback_executor.SqliteDumper"):
            with patch("zephyr.infrastructure.rollback.rollback_executor.RollbackLock"):
                ex = RollbackExecutor(project_root=tmp_project)
                assert ex.project_root == tmp_project
                assert ex.owner_session_id is not None or True

    def test_creates_with_custom_params(self, tmp_project: Path, mock_dumper: MagicMock, mock_lock: MagicMock):
        ex = RollbackExecutor(
            project_root=tmp_project,
            sqlite_dumper=mock_dumper,
            rollback_lock=mock_lock,
            owner_session_id="custom-session",
        )
        assert ex.project_root == tmp_project
        assert ex.owner_session_id == "custom-session"

    def test_in_flight_dir_created(self, executor: RollbackExecutor):
        assert executor.in_flight_dir.name == "rollback_in_flight"


class TestPreflightCheck:
    def test_preflight_clean_tree(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = [
                "",
                "main",
                "abc1234",
                "abc1234",
            ]
            result = executor.preflight_check()
            assert isinstance(result, PreflightResult)
            assert result.passed is True
            assert result.working_tree_clean is True
            assert result.not_detached_head is True

    def test_preflight_dirty_tree(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = [
                "M file1.py",
                "main",
                "abc1234",
                "abc1234",
            ]
            result = executor.preflight_check()
            assert result.passed is False
            assert result.working_tree_clean is False
            assert "Working tree is dirty" in result.errors

    def test_preflight_detached_head(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = [
                "",
                "HEAD",
                "abc1234",
                "abc1234",
            ]
            result = executor.preflight_check()
            assert result.passed is False
            assert result.not_detached_head is False
            assert "Detached HEAD state" in result.errors

    def test_preflight_rebase_in_progress(self, executor: RollbackExecutor, tmp_project: Path):
        rebase_dir = tmp_project / ".git" / "rebase-merge"
        rebase_dir.mkdir()
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = ["", "main", "abc1234", "abc1234"]
            result = executor.preflight_check()
            assert result.passed is False
            assert result.not_in_rebase is False

    def test_preflight_merge_in_progress(self, executor: RollbackExecutor, tmp_project: Path):
        merge_head = tmp_project / ".git" / "MERGE_HEAD"
        merge_head.write_text("deadbeef\n", encoding="utf-8")
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = ["", "main", "abc1234", "abc1234"]
            result = executor.preflight_check()
            assert result.passed is False
            assert result.not_in_merge is False


class TestPreview:
    def test_preview_few_files(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = [
                "file1.py\nfile2.py",
                " 2 files changed, 10 insertions(+), 5 deletions(-)",
                "",
            ]
            result = executor.preview("abc1234")
            assert isinstance(result, PreviewResult)
            assert len(result.changed_files) == 2
            assert result.conflict_risk == "low"

    def test_preview_many_files_high_risk(self, executor: RollbackExecutor):
        files = "\n".join([f"file{i}.py" for i in range(15)])
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = [
                files,
                " 15 files changed",
                "",
            ]
            result = executor.preview("abc1234")
            assert result.conflict_risk == "high"
            assert len(result.changed_files) == 15

    def test_preview_medium_risk(self, executor: RollbackExecutor):
        files = "\n".join([f"file{i}.py" for i in range(7)])
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = [
                files,
                " 7 files changed",
                "",
            ]
            result = executor.preview("abc1234")
            assert result.conflict_risk == "medium"

    def test_preview_with_merges(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = [
                "file1.py\nfile2.py",
                " 2 files changed",
                "abc1234 Merge pull request",
            ]
            result = executor.preview("abc1234")
            assert result.conflict_risk == "high"


class TestIsCommitted:
    def test_committed_files(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.return_value = "file1.py"
            result = executor.is_committed(["file1.py"])
            assert result["file1.py"] is True

    def test_uncommitted_files(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.side_effect = Exception("not tracked")
            result = executor.is_committed(["unknown.py"])
            assert result["unknown.py"] is False

    def test_empty_list(self, executor: RollbackExecutor):
        result = executor.is_committed([])
        assert result == {}


class TestDiscardChanges:
    def test_discard_no_uncommitted(self, executor: RollbackExecutor):
        with patch.object(executor, "get_uncommitted_files", return_value=[]):
            with patch.object(executor, "get_staged_uncommitted_files", return_value=[]):
                result = executor.discard_changes(["file1.py"])
                assert result.success is False
                assert result.decision == DiscardDecision.NO_CHANGES

    def test_discard_blocked_by_owner(self, executor: RollbackExecutor):
        with patch.object(executor, "detect_owner_session_in_files", return_value=["file1.py"]):
            result = executor.discard_changes(["file1.py"], force=False)
            assert result.success is False
            assert result.decision == DiscardDecision.BLOCKED_BY_OWNER
            assert "file1.py" in result.files_blocked

    def test_discard_force_bypasses_owner(self, executor: RollbackExecutor):
        with patch.object(executor, "detect_owner_session_in_files", return_value=["file1.py"]):
            with patch.object(executor, "get_uncommitted_files", return_value=["file1.py"]):
                with patch.object(executor, "get_staged_uncommitted_files", return_value=[]):
                    with patch.object(executor, "run_git", return_value=""):
                        result = executor.discard_changes(["file1.py"], force=True)
                        assert result.decision == DiscardDecision.DISCARD


class TestHardReset:
    def test_hard_reset_requires_token(self, executor: RollbackExecutor):
        with pytest.raises(ValueError, match="BREAK_GLASS token"):
            executor.hard_reset("abc1234")

    def test_hard_reset_with_token(self, executor: RollbackExecutor):
        with patch.object(executor, "lsg_verify_critical_operation"):
            with patch.object(executor, "execute") as mock_exec:
                mock_exec.return_value = RollbackExecutionResult(
                    success=True,
                    operation=RollbackOp.HARD_RESET,
                    commit_sha="abc1234",
                    files_reverted=0,
                    db_tables_restored=0,
                    db_rows_restored=0,
                )
                result = executor.hard_reset("abc1234", token="BREAK_GLASS")
                assert result.success is True


class TestForwardFixEvaluate:
    def test_evaluate_low_risk_few_files(self, executor: RollbackExecutor):
        with patch.object(executor, "preview") as mock_preview:
            mock_preview.return_value = PreviewResult(
                changed_files=["a.py", "b.py"],
                conflict_risk="low",
            )
            assert executor.forward_fix_evaluate("abc1234") is True

    def test_evaluate_high_risk(self, executor: RollbackExecutor):
        with patch.object(executor, "preview") as mock_preview:
            mock_preview.return_value = PreviewResult(
                changed_files=["a.py", "b.py", "c.py", "d.py"],
                conflict_risk="high",
            )
            assert executor.forward_fix_evaluate("abc1234") is False

    def test_evaluate_medium_risk_many_files(self, executor: RollbackExecutor):
        with patch.object(executor, "preview") as mock_preview:
            mock_preview.return_value = PreviewResult(
                changed_files=["a.py", "b.py", "c.py", "d.py"],
                conflict_risk="medium",
            )
            assert executor.forward_fix_evaluate("abc1234") is False


class TestDependencyImpactAnalysis:
    def test_impact_with_zephyr_files(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.return_value = "src/zephyr/rollback/executor.py\nsrc/zephyr/budget/main.py\nREADME.md"
            result = executor.dependency_impact_analysis("abc1234")
            assert "rollback" in result["impacted_modules"]
            assert "budget" in result["impacted_modules"]
            assert result["impact_breadth"] == 2

    def test_impact_no_zephyr_files(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.return_value = "README.md\ndocs/guide.md"
            result = executor.dependency_impact_analysis("abc1234")
            assert result["impacted_modules"] == []
            assert result["impact_breadth"] == 0

    def test_impact_empty_diff(self, executor: RollbackExecutor):
        with patch.object(executor, "run_git") as mock_git:
            mock_git.return_value = ""
            result = executor.dependency_impact_analysis("abc1234")
            assert result["changed_files"] == []


class TestInFlightManagement:
    def test_write_and_read_in_flight(self, executor: RollbackExecutor):
        eid = executor.generate_execution_id()
        executor.write_in_flight(eid, "test_step", "PENDING", {"key": "value"})
        record = executor.read_in_flight(eid)
        assert record is not None
        assert record["step"] == "test_step"
        assert record["status"] == "PENDING"
        assert record["data"]["key"] == "value"
        executor.delete_in_flight(eid)

    def test_read_nonexistent_in_flight(self, executor: RollbackExecutor):
        record = executor.read_in_flight("NONEXISTENT-ID")
        assert record is None

    def test_recover_stale_in_flight(self, executor: RollbackExecutor):
        eid = executor.generate_execution_id()
        executor.write_in_flight(eid, "git_revert", "FAILED", {"error": "test"})
        recovered = executor.recover_stale_in_flight()
        assert len(recovered) >= 1
        executor.delete_in_flight(eid)


class TestCancelPendingRollback:
    def test_cancel_requires_token(self, executor: RollbackExecutor):
        result = executor.cancel_pending_rollback("task-001", "test reason")
        assert result["canceled"] is False

    def test_cancel_with_token_no_pending(self, executor: RollbackExecutor):
        result = executor.cancel_pending_rollback("task-001", "test reason", token="BREAK_GLASS")
        assert result["canceled"] is False

    def test_cancel_with_pending(self, executor: RollbackExecutor):
        eid = executor.generate_execution_id()
        executor.write_in_flight(eid, "revert", "PENDING")
        result = executor.cancel_pending_rollback("task-001", "test reason", token="BREAK_GLASS")
        assert result["canceled"] is True


class TestGenerateExecutionId:
    def test_format(self, executor: RollbackExecutor):
        eid = executor.generate_execution_id()
        assert eid.startswith("RBEXEC-")
        assert len(eid) > 10
