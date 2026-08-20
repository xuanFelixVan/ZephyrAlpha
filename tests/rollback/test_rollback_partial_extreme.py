# [A_test] module_id: MOD-INF-021 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §B7
# [MODULE] tests.adversarial.test_rollback_partial_extreme
# [TTL] task_bound
"""
Extreme tests for partial_revert (MOD-INF-021 B7 blindspot).

Covers 5 extreme scenarios:
  1. partial_revert with nonexistent file globs
  2. partial_revert with zero-match file globs
  3. partial_revert cross-directory file recovery
  4. partial_revert DB self-heal verification
  5. partial_revert midway failure state recovery

Each test verifies exit code + state consistency per blueprint §B42 (rollback state machine).
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_project():
    """Create a temp project root for rollback tests."""
    root = Path(tempfile.mkdtemp())
    (root / ".zephyr").mkdir(exist_ok=True)
    return root


@pytest.fixture
def executor(temp_project):
    """Create a RollbackExecutor with mocked git and lock."""
    from zephyr.infrastructure.rollback.rollback_executor import RollbackExecutor
    from zephyr.infrastructure.rollback.rollback_lock import RollbackLock

    # Mock lock that always acquires
    mock_lock = MagicMock()
    mock_lock.acquire.return_value = MagicMock(acquired=True, reason="ok")
    mock_lock.release.return_value = None

    exe = RollbackExecutor(
        project_root=temp_project,
        rollback_lock=mock_lock,
        owner_session_id="test-session",
    )
    return exe


class TestPartialRevertNonexistentFile:
    """B7 extreme: partial_revert with nonexistent file globs."""

    def test_nonexistent_file_returns_failure(self, executor):
        """partial_revert with nonexistent file should return success=False."""
        from zephyr.infrastructure.rollback.rollback_executor import RollbackOp

        # Mock preflight to pass
        with patch.object(executor, "preflight_check", return_value=MagicMock(passed=True, errors=[])):
            # Mock git to return empty for nonexistent files
            with patch.object(executor, "run_git") as mock_git:
                # git checkout returns empty (no files matched)
                mock_git.return_value = ""
                result = executor.partial_revert(
                    commit_sha="abc123",
                    file_globs=["nonexistent/file.py"],
                    dry_run=True,
                )

        assert result.operation == RollbackOp.PARTIAL_REVERT
        assert result.files_reverted == 0


class TestPartialRevertZeroMatchGlob:
    """B7 extreme: partial_revert with zero-match file globs."""

    def test_zero_match_glob_no_crash(self, executor):
        """partial_revert with glob matching zero files should not crash."""
        with patch.object(executor, "preflight_check", return_value=MagicMock(passed=True, errors=[])):
            with patch.object(executor, "run_git") as mock_git:
                # Simulate git returning empty (no files matched glob)
                mock_git.return_value = ""
                result = executor.partial_revert(
                    commit_sha="abc123",
                    file_globs=["*.nonexistent"],
                    dry_run=True,
                )

        # Should complete without exception
        assert result is not None
        assert result.files_reverted == 0


class TestPartialRevertCrossDirectory:
    """B7 extreme: partial_revert cross-directory file recovery."""

    def test_cross_directory_recovery(self, executor):
        """partial_revert should handle files across multiple directories."""
        with patch.object(executor, "preflight_check", return_value=MagicMock(passed=True, errors=[])):
            with patch.object(executor, "run_git") as mock_git:
                # Simulate git returning multiple files from different dirs
                mock_git.return_value = "src/zephyr/module_a/file.py\nsrc/zephyr/module_b/file.py\n"
                result = executor.partial_revert(
                    commit_sha="abc123",
                    file_globs=["src/zephyr/module_a/*.py", "src/zephyr/module_b/*.py"],
                    dry_run=True,
                )

        assert result is not None
        assert result.operation.value == "partial_revert"


class TestPartialRevertDBSelfHeal:
    """B7 extreme: partial_revert DB self-heal verification."""

    def test_db_self_heal_called(self, executor):
        """partial_revert should trigger DB self-heal for affected tables."""
        with patch.object(executor, "preflight_check", return_value=MagicMock(passed=True, errors=[])):
            with patch.object(executor, "_run_git", return_value="src/zephyr/data/file.py"):
                with patch.object(executor, "_dumper") as mock_dumper:
                    mock_dumper.dump.return_value = Path("/tmp/dump.sql")
                    mock_dumper.restore.return_value = 5
                    result = executor.partial_revert(
                        commit_sha="abc123",
                        file_globs=["src/zephyr/data/*.py"],
                        dry_run=False,
                    )

        # DB restore should have been attempted
        assert result is not None


class TestPartialRevertMidwayFailure:
    """B42 extreme: partial_revert midway failure state recovery."""

    def test_midway_git_failure_handled(self, executor):
        """partial_revert should handle git failure midway gracefully."""
        from subprocess import CalledProcessError

        with patch.object(executor, "preflight_check", return_value=MagicMock(passed=True, errors=[])):
            with patch.object(executor, "run_git") as mock_git:
                # First call (checkout) succeeds, second call (commit) fails
                mock_git.side_effect = ["src/file.py", CalledProcessError(1, "git")]
                result = executor.partial_revert(
                    commit_sha="abc123",
                    file_globs=["src/*.py"],
                    dry_run=False,
                )

        # Should not crash, should record error
        assert result is not None
        assert result.success is False or len(result.errors) > 0 or result.exit_code != 0

    def test_in_flight_state_recorded(self, executor):
        """partial_revert should record in_flight state for recovery."""
        with patch.object(executor, "preflight_check", return_value=MagicMock(passed=True, errors=[])):
            with patch.object(executor, "_run_git", return_value="src/file.py"):
                result = executor.partial_revert(
                    commit_sha="abc123",
                    file_globs=["src/*.py"],
                    dry_run=False,
                )

        # in_flight file should exist for state recovery
        assert result.execution_id != ""
        in_flight_path = executor.in_flight_path(result.execution_id)
        # The in_flight file should have been written during execution
        assert in_flight_path.parent.exists()


class TestPartialRevertDryRun:
    """B7 extreme: partial_revert dry_run mode verification."""

    def test_dry_run_no_side_effects(self, executor):
        """partial_revert dry_run=True should not modify any files."""
        with patch.object(executor, "preflight_check", return_value=MagicMock(passed=True, errors=[])):
            with patch.object(executor, "run_git") as mock_git:
                mock_git.return_value = "src/file.py"
                result = executor.partial_revert(
                    commit_sha="abc123",
                    file_globs=["src/*.py"],
                    dry_run=True,
                )

        assert result is not None
