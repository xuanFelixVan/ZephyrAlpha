# [A_test] module_id: MOD-GOV_rollback_bootstrap | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_bootstrap
# [INVARIANTS] bootstrap_rollback returns int exit code; bootstrap_from_failure_log returns int exit code
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit codes: 0=success; 1=git unavailable; 2=no commits; 3=revert conflict
# [TESTS] tests/test_rollback_bootstrap.py
# [TTL] task_bound

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.infrastructure.rollback.rollback_bootstrap import (
    _check_git_available,
    _get_recent_commits,
    _git,
    _git_head_short,
    _git_revert,
    _git_status_clean,
    bootstrap_from_failure_log,
    bootstrap_rollback,
)


class TestGitHelper:
    def test_git_returns_completed_process(self):
        result = _git(["--version"])
        assert isinstance(result, subprocess.CompletedProcess)

    def test_git_with_timeout(self):
        result = _git(["--version"], timeout=30)
        assert result.returncode == 0

    def test_git_invalid_args_returns_nonzero(self):
        result = _git(["nonexistent-arg-xyz"])
        assert result.returncode != 0


class TestCheckGitAvailable:
    def test_git_available(self):
        assert _check_git_available() is True

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git")
    def test_git_not_available(self, mock_git):
        mock_git.return_value = MagicMock(returncode=1)
        assert _check_git_available() is False


class TestGetRecentCommits:
    def test_returns_list_of_strings(self, tmp_path: Path):
        commits = _get_recent_commits(tmp_path)
        assert isinstance(commits, list)

    def test_returns_at_most_count_commits(self, tmp_path: Path):
        commits = _get_recent_commits(tmp_path, count=3)
        assert len(commits) <= 3

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git")
    def test_returns_empty_on_git_failure(self, mock_git):
        mock_git.return_value = MagicMock(returncode=1, stdout="")
        result = _get_recent_commits(Path("/nonexistent"), count=5)
        assert result == []

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git")
    def test_parses_oneline_output(self, mock_git):
        mock_git.return_value = MagicMock(returncode=0, stdout="abc1234 msg1\ndef5678 msg2\n")
        result = _get_recent_commits(Path("/tmp"), count=5)
        assert result == ["abc1234", "def5678"]


class TestGitRevert:
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git")
    def test_revert_success(self, mock_git):
        mock_git.return_value = MagicMock(returncode=0)
        assert _git_revert(Path("/tmp"), "abc1234") is True

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git")
    def test_revert_conflict(self, mock_git):
        mock_git.return_value = MagicMock(returncode=1)
        assert _git_revert(Path("/tmp"), "abc1234") is False


class TestGitStatusClean:
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git")
    def test_clean_working_tree(self, mock_git):
        mock_git.return_value = MagicMock(returncode=0, stdout="")
        assert _git_status_clean(Path("/tmp")) is True

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git")
    def test_dirty_working_tree(self, mock_git):
        mock_git.return_value = MagicMock(returncode=0, stdout="M file.py\n")
        assert _git_status_clean(Path("/tmp")) is False


class TestGitHeadShort:
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git")
    def test_returns_short_sha(self, mock_git):
        mock_git.return_value = MagicMock(returncode=0, stdout="abc1234\n")
        assert _git_head_short(Path("/tmp")) == "abc1234"

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git")
    def test_returns_empty_on_failure(self, mock_git):
        mock_git.return_value = MagicMock(returncode=128, stdout="")
        assert _git_head_short(Path("/tmp")) == ""


class TestBootstrapRollback:
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._check_git_available", return_value=False)
    def test_returns_1_when_git_unavailable(self, mock_check):
        assert bootstrap_rollback() == 1

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._check_git_available", return_value=True)
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._get_recent_commits", return_value=[])
    def test_returns_2_when_no_commits(self, mock_commits, mock_check):
        assert bootstrap_rollback() == 2

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._check_git_available", return_value=True)
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._get_recent_commits", return_value=["abc1234"])
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_revert", return_value=False)
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_head_short", return_value="def5678")
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_status_clean", return_value=True)
    def test_returns_3_on_revert_conflict(self, mock_clean, mock_head, mock_revert, mock_commits, mock_check):
        assert bootstrap_rollback() == 3

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._check_git_available", return_value=True)
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_revert", return_value=True)
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_head_short", return_value="def5678")
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_status_clean", return_value=True)
    def test_returns_0_on_success_with_explicit_commit(self, mock_clean, mock_head, mock_revert, mock_check):
        assert bootstrap_rollback(commit_sha="abc1234") == 0

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._check_git_available", return_value=True)
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_revert", return_value=True)
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_head_short", return_value="def5678")
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_status_clean", return_value=True)
    def test_uses_project_root_when_provided(self, mock_clean, mock_head, mock_revert, mock_check):
        root = Path("/some/project")
        result = bootstrap_rollback(project_root=root, commit_sha="abc1234")
        assert result == 0

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._check_git_available", return_value=True)
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_revert", return_value=True)
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_head_short", return_value="def5678")
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap._git_status_clean", return_value=False)
    def test_returns_0_even_with_dirty_tree(self, mock_clean, mock_head, mock_revert, mock_check):
        assert bootstrap_rollback(commit_sha="abc1234") == 0


class TestBootstrapFromFailureLog:
    @patch("zephyr.infrastructure.rollback.rollback_bootstrap.bootstrap_rollback", return_value=0)
    def test_no_failure_log_falls_back_to_normal(self, mock_rollback, tmp_path: Path):
        log_path = tmp_path / "nonexistent.json"
        result = bootstrap_from_failure_log(log_path)
        assert result == 0
        mock_rollback.assert_called_once_with()

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap.bootstrap_rollback", return_value=0)
    def test_escalated_after_3_failures(self, mock_rollback, tmp_path: Path):
        log_data = {"consecutive_failures": 3, "last_known_good_commit": "abc1234"}
        log_path = tmp_path / "failure_log.json"
        log_path.write_text(json.dumps(log_data), encoding="utf-8")
        result = bootstrap_from_failure_log(log_path)
        assert result == 0
        mock_rollback.assert_called_once_with(commit_sha="abc1234")

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap.bootstrap_rollback", return_value=0)
    def test_below_threshold_falls_back(self, mock_rollback, tmp_path: Path):
        log_data = {"consecutive_failures": 2, "last_known_good_commit": "abc1234"}
        log_path = tmp_path / "failure_log.json"
        log_path.write_text(json.dumps(log_data), encoding="utf-8")
        result = bootstrap_from_failure_log(log_path)
        assert result == 0
        mock_rollback.assert_called_once_with()

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap.bootstrap_rollback", return_value=0)
    def test_malformed_json_falls_back(self, mock_rollback, tmp_path: Path):
        log_path = tmp_path / "failure_log.json"
        log_path.write_text("{invalid json", encoding="utf-8")
        result = bootstrap_from_failure_log(log_path)
        assert result == 0
        mock_rollback.assert_called_once_with()

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap.bootstrap_rollback", return_value=0)
    def test_missing_commit_key_falls_back(self, mock_rollback, tmp_path: Path):
        log_data = {"consecutive_failures": 3}
        log_path = tmp_path / "failure_log.json"
        log_path.write_text(json.dumps(log_data), encoding="utf-8")
        result = bootstrap_from_failure_log(log_path)
        assert result == 0
        mock_rollback.assert_called_once_with()

    @patch("zephyr.infrastructure.rollback.rollback_bootstrap.bootstrap_rollback", return_value=0)
    def test_empty_commit_falls_back(self, mock_rollback, tmp_path: Path):
        log_data = {"consecutive_failures": 3, "last_known_good_commit": ""}
        log_path = tmp_path / "failure_log.json"
        log_path.write_text(json.dumps(log_data), encoding="utf-8")
        result = bootstrap_from_failure_log(log_path)
        assert result == 0
        mock_rollback.assert_called_once_with()
