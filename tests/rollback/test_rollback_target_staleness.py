# [A_test] module_id: MOD-GOV_rollback_target_staleness | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §7
# [MODULE] tests.test_rollback_target_staleness
# [INVARIANTS] EXIT_CODE_STALE=42; MAX_AGE_DAYS=30
# [MODIFY-GUARD] Do not change test data without updating source module
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StalenessResult always returned even on git failure
# [TESTS] pytest tests/test_rollback_target_staleness.py -q
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.infrastructure.rollback.rollback_target_staleness import (
    RollbackTargetStaleness,
    StalenessResult,
)


class TestInstantiation:
    def test_default_project_root(self):
        checker = RollbackTargetStaleness()
        assert checker.project_root == Path.cwd()

    def test_custom_project_root(self):
        root = Path("/tmp/fake_project")
        checker = RollbackTargetStaleness(project_root=root)
        assert checker.project_root == root

    def test_none_project_root_defaults_to_cwd(self):
        checker = RollbackTargetStaleness(project_root=None)
        assert checker.project_root == Path.cwd()


class TestCheckFreshCommit:
    def test_fresh_commit_not_stale(self):
        checker = RollbackTargetStaleness(project_root=Path.cwd())
        recent_date = datetime.now(UTC) - timedelta(days=5)
        with patch.object(checker, "_get_commit_date", return_value=recent_date):
            result = checker.check("abc1234")
        assert result.is_stale is False
        assert result.exit_code == 0
        assert result.age_days > 4
        assert result.recommendation == ""

    def test_just_under_30_days_not_stale(self):
        checker = RollbackTargetStaleness(project_root=Path.cwd())
        just_under = datetime.now(UTC) - timedelta(days=29, hours=23)
        with patch.object(checker, "_get_commit_date", return_value=just_under):
            result = checker.check("abc1234")
        assert result.is_stale is False
        assert result.exit_code == 0


class TestCheckStaleCommit:
    def test_stale_commit_triggers_exit_42(self):
        checker = RollbackTargetStaleness(project_root=Path.cwd())
        old_date = datetime.now(UTC) - timedelta(days=60)
        with patch.object(checker, "_get_commit_date", return_value=old_date):
            result = checker.check("deadbeef")
        assert result.is_stale is True
        assert result.exit_code == 42
        assert "60" in result.recommendation
        assert "deadbeef" in result.recommendation
        assert result.last_verified_at != ""


class TestCheckCommitDateUnavailable:
    def test_git_failure_returns_safe_result(self):
        checker = RollbackTargetStaleness(project_root=Path.cwd())
        with patch.object(checker, "_get_commit_date", return_value=None):
            result = checker.check("missing")
        assert result.is_stale is False
        assert result.exit_code == 0
        assert result.age_days == 0
        assert "Could not determine" in result.recommendation


class TestGetCommitDate:
    def test_successful_git_call(self):
        checker = RollbackTargetStaleness(project_root=Path.cwd())
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "2026-01-15T10:30:00+00:00\n"
        with patch(
            "zephyr.infrastructure.rollback.rollback_target_staleness.run_subprocess_hidden", return_value=mock_result
        ):
            dt = checker.get_commit_date("abc123")
        assert dt is not None
        assert dt.year == 2026

    def test_git_returns_nonzero(self):
        checker = RollbackTargetStaleness(project_root=Path.cwd())
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        with patch(
            "zephyr.infrastructure.rollback.rollback_target_staleness.run_subprocess_hidden", return_value=mock_result
        ):
            dt = checker.get_commit_date("bad_sha")
        assert dt is None

    def test_git_exception_returns_none(self):
        checker = RollbackTargetStaleness(project_root=Path.cwd())
        with patch(
            "zephyr.infrastructure.rollback.rollback_target_staleness.run_subprocess_hidden",
            side_effect=Exception("no git"),
        ):
            dt = checker.get_commit_date("abc")
        assert dt is None

    def test_empty_stdout_returns_none(self):
        checker = RollbackTargetStaleness(project_root=Path.cwd())
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "   \n"
        with patch(
            "zephyr.infrastructure.rollback.rollback_target_staleness.run_subprocess_hidden", return_value=mock_result
        ):
            dt = checker.get_commit_date("abc")
        assert dt is None


class TestConstants:
    def test_exit_code_stale(self):
        assert RollbackTargetStaleness.EXIT_CODE_STALE == 42

    def test_max_age_days(self):
        assert RollbackTargetStaleness.MAX_AGE_DAYS == 30


class TestStalenessResult:
    def test_dataclass_fields(self):
        r = StalenessResult(
            commit_sha="abc",
            age_days=45.0,
            is_stale=True,
            last_verified_at="2026-01-01",
            exit_code=42,
            recommendation="stale",
        )
        assert r.commit_sha == "abc"
        assert r.age_days == 45.0
        assert r.is_stale is True
        assert r.exit_code == 42
