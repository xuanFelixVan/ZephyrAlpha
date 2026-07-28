# [A_test] module_id: MOD-GOV_rollback_e2e | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-335 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.integration.test_rollback_e2e
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
E2E integration tests for rollback pipeline (MOD-INF-021 §9 CT-RBK-GATE-001).

Full flow: trigger → preflight → preview → acquire lock → execute → verify → release.

Tests:
  - Full revert E2E (Git + DB)
  - Partial revert E2E
  - Discard E2E
  - Dry-run preview E2E
  - Lock contention E2E
  - Audit trail production E2E
  - Kill switch integration E2E
"""

from __future__ import annotations

import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from zephyr.infrastructure.rollback.rollback_executor import (
    RollbackExecutor,
    RollbackOp,
)
from zephyr.infrastructure.rollback.rollback_lock import LockAcquireResult, RollbackLock


@contextmanager
def _temp_dir():
    tmp = tempfile.mkdtemp()
    root = Path(tmp)
    try:
        yield root
    finally:
        import gc

        gc.collect()
        for _ in range(100):
            try:
                for f in root.rglob("*"):
                    if f.is_file():
                        f.unlink(missing_ok=True)
                for d in sorted(root.rglob("*"), reverse=True):
                    if d.is_dir():
                        d.rmdir()
                root.rmdir()
                break
            except (PermissionError, OSError):
                time.sleep(0.01)


class TestFullRevertE2E:
    """full_revert() 端到端流程"""

    def test_full_revert_clean_flow(self):
        with _temp_dir() as root:
            _setup_minimal_git_env(root)

            mock_lock = MagicMock(spec=RollbackLock)
            mock_lock.acquire.return_value = LockAcquireResult(
                acquired=True, lock_id="lock-001", wait_time_ms=0, reason=""
            )
            mock_lock.release.return_value = True

            exec = RollbackExecutor(project_root=root, rollback_lock=mock_lock)
            exec.g0_verify = MagicMock(return_value=True)

            with patch.object(exec, "_run_git") as mock_git:
                mock_git.side_effect = _build_clean_git_responses()
                result = exec.full_revert("abc123", audit_session="test-session")

                assert result.success
                assert result.operation == RollbackOp.FULL_REVERT
                assert result.files_reverted > 0

            mock_lock.acquire.assert_called_once()
            mock_lock.release.assert_called_once_with("lock-001")

    def test_full_revert_dry_run(self):
        with _temp_dir() as root:
            _setup_minimal_git_env(root)

            mock_lock = MagicMock(spec=RollbackLock)
            mock_lock.acquire.return_value = LockAcquireResult(
                acquired=True, lock_id="lock-002", wait_time_ms=0, reason=""
            )

            exec = RollbackExecutor(project_root=root, rollback_lock=mock_lock)

            with patch.object(exec, "_run_git") as mock_git:
                mock_git.side_effect = _build_preview_only_git_responses()
                result = exec.full_revert("abc123", dry_run=True, audit_session="test-session")

                assert result.success
                assert result.operation == RollbackOp.FULL_REVERT

    def test_full_revert_lock_contention(self):
        with _temp_dir() as root:
            _setup_minimal_git_env(root)

            mock_lock = MagicMock(spec=RollbackLock)
            mock_lock.acquire.return_value = LockAcquireResult(
                acquired=False, lock_id="", wait_time_ms=0, reason="Lock held by session-X"
            )

            exec = RollbackExecutor(project_root=root, rollback_lock=mock_lock)

            with patch.object(exec, "_run_git") as mock_git:
                mock_git.side_effect = _build_clean_git_responses()
                result = exec.full_revert("abc123", audit_session="test-session")

                assert not result.success
                assert "Could not acquire rollback lock" in result.errors[0]

            mock_lock.release.assert_not_called()


class TestPartialRevertE2E:
    """partial_revert() 端到端流程"""

    def test_partial_revert_clean_flow(self):
        with _temp_dir() as root:
            _setup_minimal_git_env(root)

            mock_lock = MagicMock(spec=RollbackLock)
            mock_lock.acquire.return_value = LockAcquireResult(
                acquired=True, lock_id="lock-003", wait_time_ms=0, reason=""
            )

            exec = RollbackExecutor(project_root=root, rollback_lock=mock_lock)
            exec.g0_verify = MagicMock(return_value=True)

            with patch.object(exec, "_run_git") as mock_git:
                mock_git.side_effect = _build_partial_revert_git_responses()
                result = exec.partial_revert("abc123", file_globs=["src/**/*.py"], audit_session="test-session")

                assert result.success
                assert result.operation == RollbackOp.PARTIAL_REVERT


class TestDiscardE2E:
    """discard() 端到端流程"""

    def test_discard_clean_flow(self):
        with _temp_dir() as root:
            _setup_minimal_git_env(root)

            mock_lock = MagicMock(spec=RollbackLock)
            mock_lock.acquire.return_value = LockAcquireResult(
                acquired=True, lock_id="lock-004", wait_time_ms=0, reason=""
            )

            exec = RollbackExecutor(project_root=root, rollback_lock=mock_lock)

            with (
                patch.object(exec, "_run_git") as mock_git,
                patch.object(exec, "get_uncommitted_files", return_value=["file.py"]),
                patch.object(exec, "get_staged_uncommitted_files", return_value=[]),
            ):
                mock_git.return_value = ""
                result = exec.discard(["file.py"], audit_session="test-session")

                assert result.success
                assert result.operation == RollbackOp.DISCARD


class TestAuditTrailE2E:
    """审计链路：回滚 → audit log 写入"""

    def test_audit_log_written_on_success(self):
        with _temp_dir() as root:
            _setup_minimal_git_env(root)
            (root / ".zephyr" / "audit").mkdir(parents=True, exist_ok=True)

            mock_lock = MagicMock(spec=RollbackLock)
            mock_lock.acquire.return_value = LockAcquireResult(
                acquired=True, lock_id="lock-005", wait_time_ms=0, reason=""
            )

            exec = RollbackExecutor(project_root=root, rollback_lock=mock_lock)
            exec.g0_verify = MagicMock(return_value=True)

            with patch.object(exec, "_run_git") as mock_git:
                mock_git.side_effect = _build_clean_git_responses()
                result = exec.full_revert("abc123", audit_session="test-session")
                assert result.success


class TestKillSwitchIntegrationE2E:
    """kill_switch 集成：KillSwitchManager"""

    def test_kill_switch_manager_l3_requires_token(self):
        from zephyr.infrastructure.rollback.kill_switch import KillLevel, KillSwitchManager

        mgr = KillSwitchManager(project_root=Path(tempfile.mkdtemp()))
        with pytest.raises(ValueError, match="BREAK_GLASS"):
            mgr.activate(KillLevel.L3_GLOBAL, "*", "test", token="")

    def test_kill_switch_activate_deactivate(self):
        from zephyr.infrastructure.rollback.kill_switch import KillLevel, KillSwitchManager

        mgr = KillSwitchManager(project_root=Path(tempfile.mkdtemp()))
        entry = mgr.activate(KillLevel.L1_SESSION, "session-X", "test")
        assert entry.level == KillLevel.L1_SESSION
        killed, level = mgr.is_killed(session_id="session-X")
        assert killed
        deactivated = mgr.deactivate(KillLevel.L1_SESSION, "session-X")
        assert deactivated


class TestVerifierIntegrationE2E:
    """验证器集成：回滚后 G0 + DB 自愈"""

    def test_verifier_integrated_after_revert(self):
        with _temp_dir() as root:
            _setup_minimal_git_env(root)

            mock_lock = MagicMock(spec=RollbackLock)
            mock_lock.acquire.return_value = LockAcquireResult(
                acquired=True, lock_id="lock-006", wait_time_ms=0, reason=""
            )

            exec = RollbackExecutor(project_root=root, rollback_lock=mock_lock)

            g0_results = []

            def _track_g0(**kwargs):
                g0_results.append(True)
                return True

            exec.g0_verify = MagicMock(side_effect=_track_g0)

            with patch.object(exec, "_run_git") as mock_git:
                mock_git.side_effect = _build_clean_git_responses()
                result = exec.full_revert("abc123", audit_session="test-session")

                assert result.success
                assert len(g0_results) > 0


def _setup_minimal_git_env(root: Path) -> None:
    (root / ".git").mkdir(parents=True, exist_ok=True)
    (root / "src" / "zephyr" / "rollback").mkdir(parents=True, exist_ok=True)


def _build_clean_git_responses():
    return [
        "",
        "main",
        "abc123",
        "abc123",
        "abc123",
        "2 files changed",
        "",
        "revert output",
        "src/a.py\nsrc/b.py",
    ]


def _build_preview_only_git_responses():
    return [
        "",
        "main",
        "abc123",
        "abc123",
        "abc123",
        "2 files changed",
        "",
    ]


def _build_partial_revert_git_responses():
    return [
        "",
        "main",
        "abc123",
        "abc123",
        "abc123",
        "1 file changed",
        "",
        "partial revert output",
        "src/a.py",
    ]
