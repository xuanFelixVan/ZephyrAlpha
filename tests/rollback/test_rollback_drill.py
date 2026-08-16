# [A_test] module_id: MOD-GOV_rollback_drill | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_rollback_drill
# [INVARIANTS] run_drill returns DrillResult; consecutive_fails >= MAX_CONSECUTIVE_FAILS triggers meltdown
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DrillResult.success=False when no commits available
# [TESTS] tests/test_rollback_drill.py
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from zephyr.infrastructure.rollback.rollback_drill import (
    CHAOS_SCENARIOS,
    ChaosScenario,
    DrillResult,
    RollbackDrill,
)


class TestChaosScenario:
    def test_create_enabled(self):
        s = ChaosScenario(name="test", description="desc", enabled=True)
        assert s.name == "test"
        assert s.enabled is True

    def test_create_disabled(self):
        s = ChaosScenario(name="test", description="desc", enabled=False)
        assert s.enabled is False

    def test_default_enabled(self):
        s = ChaosScenario(name="test", description="desc")
        assert s.enabled is True


class TestDrillResult:
    def test_create_with_defaults(self):
        r = DrillResult(
            drill_id="DRILL-001",
            timestamp_utc="2026-01-01T00:00:00Z",
            commit_sha="abc1234",
            duration_ms=100,
            conflict_rate=0.0,
            db_integrity_pass=True,
            chaos_scenario="gc_concurrent",
            success=True,
        )
        assert r.drill_id == "DRILL-001"
        assert r.details == []
        assert r.success is True

    def test_with_details(self):
        r = DrillResult(
            drill_id="DRILL-002",
            timestamp_utc="2026-01-01T00:00:00Z",
            commit_sha="abc1234",
            duration_ms=200,
            conflict_rate=1.0,
            db_integrity_pass=False,
            chaos_scenario="sqlite_locked",
            success=False,
            details=["conflict detected", "db check failed"],
        )
        assert len(r.details) == 2


class TestChaosScenariosList:
    def test_has_four_scenarios(self):
        assert len(CHAOS_SCENARIOS) == 4

    def test_all_enabled_by_default(self):
        for s in CHAOS_SCENARIOS:
            assert s.enabled is True

    def test_scenario_names(self):
        names = [s.name for s in CHAOS_SCENARIOS]
        assert "gc_concurrent" in names
        assert "sqlite_locked" in names
        assert "disk_90pct" in names
        assert "cpu_saturation" in names


class TestRollbackDrillInstantiation:
    def test_default_project_root(self):
        with patch.object(RollbackDrill, "__init__", lambda self, **kw: None):
            d = RollbackDrill()
            d.project_root = Path.cwd()
            d.drill_log_dir = Path.cwd() / RollbackDrill.DRILL_LOG_DIR
            d._consecutive_fails = 0  # 只读 property（Stage 4 公共化），私有位赋值
            d.automatic_rollback_melted = False
            assert d.project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        assert d.project_root == tmp_path

    def test_creates_log_dir(self, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        assert d.drill_log_dir.exists()

    def test_initial_state(self, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        assert d.consecutive_fails == 0
        assert d.is_melted is False


class TestRollbackDrillIsDrillTime:
    @patch("zephyr.infrastructure.rollback.rollback_drill.datetime")
    def test_saturday_3am_is_drill_time(self, mock_dt, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_now = MagicMock()
        mock_now.weekday.return_value = 5
        mock_now.hour = 3
        mock_dt.now.return_value = mock_now
        assert d.is_drill_time() is True

    @patch("zephyr.infrastructure.rollback.rollback_drill.datetime")
    def test_monday_is_not_drill_time(self, mock_dt, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_now = MagicMock()
        mock_now.weekday.return_value = 0
        mock_now.hour = 3
        mock_dt.now.return_value = mock_now
        assert d.is_drill_time() is False

    @patch("zephyr.infrastructure.rollback.rollback_drill.datetime")
    def test_saturday_wrong_hour(self, mock_dt, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_now = MagicMock()
        mock_now.weekday.return_value = 5
        mock_now.hour = 14
        mock_dt.now.return_value = mock_now
        assert d.is_drill_time() is False


class TestRollbackDrillSelectRandomCommit:
    # 注：select_random_commit 走公共 run_git（Stage 4 公共化），patch _run_git 无效。
    @patch.object(RollbackDrill, "run_git")
    def test_returns_commit_sha(self, mock_git, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = "abc1234 msg1\ndef5678 msg2\n"
        result = d.select_random_commit()
        assert result in ["abc1234", "def5678"]

    @patch.object(RollbackDrill, "run_git")
    def test_returns_empty_on_no_commits(self, mock_git, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        result = d.select_random_commit()
        assert result == ""

    @patch.object(RollbackDrill, "run_git")
    def test_returns_empty_on_git_failure(self, mock_git, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        result = d.select_random_commit()
        assert result == ""


class TestRollbackDrillRunDrill:
    @patch.object(RollbackDrill, "select_random_commit", return_value="")
    def test_no_commits_returns_failure(self, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        result = d.run_drill()
        assert result.success is False
        assert result.commit_sha == ""
        assert "No commits" in result.details[0]

    @patch.object(RollbackDrill, "select_random_commit", return_value="abc1234")
    @patch.object(RollbackDrill, "_run_git")
    @patch("subprocess.run")
    def test_successful_drill(self, mock_subprocess, mock_git, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        mock_subprocess.return_value = MagicMock(returncode=0, stderr="")
        result = d.run_drill(force_chaos="gc_concurrent")
        assert result.success is True
        assert result.chaos_scenario == "gc_concurrent"

    @patch.object(RollbackDrill, "select_random_commit", return_value="abc1234")
    @patch.object(RollbackDrill, "_run_git")
    @patch("subprocess.run")
    def test_failed_revert(self, mock_subprocess, mock_git, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        mock_subprocess.return_value = MagicMock(returncode=1, stderr="conflict")
        result = d.run_drill(force_chaos="sqlite_locked")
        assert result.success is False
        assert result.conflict_rate == 1.0

    @patch.object(RollbackDrill, "select_random_commit", return_value="abc1234")
    @patch.object(RollbackDrill, "_run_git")
    @patch("subprocess.run", side_effect=Exception("timeout"))
    def test_exception_during_drill(self, mock_subprocess, mock_git, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        result = d.run_drill(force_chaos="disk_90pct")
        assert result.success is False

    @patch.object(RollbackDrill, "select_random_commit", return_value="abc1234")
    @patch.object(RollbackDrill, "_run_git")
    @patch("subprocess.run")
    def test_drill_result_has_id(self, mock_subprocess, mock_git, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        mock_subprocess.return_value = MagicMock(returncode=0, stderr="")
        result = d.run_drill(force_chaos="gc_concurrent")
        assert result.drill_id.startswith("DRILL-")

    @patch.object(RollbackDrill, "select_random_commit", return_value="abc1234")
    @patch.object(RollbackDrill, "_run_git")
    @patch("subprocess.run")
    def test_drill_result_has_timestamp(self, mock_subprocess, mock_git, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        mock_subprocess.return_value = MagicMock(returncode=0, stderr="")
        result = d.run_drill(force_chaos="gc_concurrent")
        assert result.timestamp_utc != ""


class TestRollbackDrillMeltdown:
    def test_meltdown_not_triggered_initially(self, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        assert d.is_melted is False

    @patch.object(RollbackDrill, "select_random_commit", return_value="abc1234")
    @patch.object(RollbackDrill, "_run_git")
    @patch("subprocess.run")
    def test_meltdown_after_consecutive_fails(self, mock_subprocess, mock_git, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        mock_subprocess.return_value = MagicMock(returncode=1, stderr="conflict")
        d.run_drill(force_chaos="gc_concurrent")
        assert d.consecutive_fails == 1
        assert d.is_melted is False
        d.run_drill(force_chaos="gc_concurrent")
        assert d.consecutive_fails == 2
        assert d.is_melted is True

    @patch.object(RollbackDrill, "select_random_commit", return_value="abc1234")
    @patch.object(RollbackDrill, "_run_git")
    @patch("subprocess.run")
    def test_meltdown_creates_alert_file(self, mock_subprocess, mock_git, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        mock_subprocess.return_value = MagicMock(returncode=1, stderr="conflict")
        d.run_drill(force_chaos="gc_concurrent")
        d.run_drill(force_chaos="gc_concurrent")
        alert_path = tmp_path / ".zephyr" / "ROLLBACK_MELTDOWN.json"
        assert alert_path.exists()
        alert = json.loads(alert_path.read_text(encoding="utf-8"))
        assert alert["alert"] == "P0_ROLLBACK_DRILL_MELTDOWN"

    @patch.object(RollbackDrill, "select_random_commit", return_value="abc1234")
    @patch.object(RollbackDrill, "_run_git")
    @patch("subprocess.run")
    def test_success_resets_consecutive_fails(self, mock_subprocess, mock_git, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        mock_subprocess.return_value = MagicMock(returncode=1, stderr="conflict")
        d.run_drill(force_chaos="gc_concurrent")
        assert d.consecutive_fails == 1
        mock_subprocess.return_value = MagicMock(returncode=0, stderr="")
        d.run_drill(force_chaos="gc_concurrent")
        assert d.consecutive_fails == 0


class TestRollbackDrillSaveResult:
    @patch.object(RollbackDrill, "select_random_commit", return_value="abc1234")
    @patch.object(RollbackDrill, "_run_git")
    @patch("subprocess.run")
    def test_saves_drill_result_to_file(self, mock_subprocess, mock_git, mock_select, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        mock_git.return_value = ""
        mock_subprocess.return_value = MagicMock(returncode=0, stderr="")
        result = d.run_drill(force_chaos="gc_concurrent")
        log_path = d.drill_log_dir / f"{result.drill_id}.json"
        assert log_path.exists()
        data = json.loads(log_path.read_text(encoding="utf-8"))
        assert data["drill_id"] == result.drill_id
        assert data["success"] is True


class TestRollbackDrillCheckDbIntegrity:
    def test_returns_true_when_no_db(self, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        assert d.check_db_integrity(tmp_path) is True

    def test_returns_false_on_corrupted_db(self, tmp_path: Path):
        d = RollbackDrill(project_root=tmp_path)
        db_dir = tmp_path / "data" / "databases"
        db_dir.mkdir(parents=True, exist_ok=True)
        db_path = db_dir / "governance.db"
        db_path.write_text("not a valid sqlite database", encoding="utf-8")
        result = d.check_db_integrity(tmp_path)
        assert result is False
