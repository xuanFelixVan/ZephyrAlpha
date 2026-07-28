# [A_test] module_id: MOD-GOV_skill_efficacy_calibrator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_efficacy_calibrator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_efficacy_calibrator.py
# [TTL] task_bound

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from zephyr.autonomy_core.skills.skill_efficacy_calibrator import (
    SkillEfficacyCalibrator,
    SkillsBenchRunner,
)


@pytest.fixture
def tmp_history(tmp_path):
    p = tmp_path / "bench_history.json"
    yield p
    if p.exists():
        p.unlink()


@pytest.fixture
def runner(tmp_history):
    return SkillsBenchRunner(history_path=tmp_history)


@pytest.fixture
def calibrator():
    return SkillEfficacyCalibrator()


class TestSkillsBenchRunnerInit:
    def test_instantiation_with_custom_path(self, tmp_history):
        r = SkillsBenchRunner(history_path=tmp_history)
        assert r.history_path == tmp_history
        assert r.history == {}

    def test_instantiation_default_path(self):
        r = SkillsBenchRunner()
        assert r.history_path is not None

    def test_load_history_corrupt_file(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("NOT JSON", encoding="utf-8")
        r = SkillsBenchRunner(history_path=bad)
        assert r.history == {}


class TestSkillsBenchRunnerRecordRun:
    def test_record_run_stores_entry(self, runner):
        runner.record_run("skill-1", 85.0, 120.5, 90.0, 4, 5)
        hist = runner.get_history("skill-1")
        assert len(hist) == 1
        assert hist[0]["score"] == 85.0
        assert hist[0]["latency_ms"] == 120.5
        assert hist[0]["accuracy"] == 90.0
        assert hist[0]["checks_passed"] == 4
        assert hist[0]["checks_total"] == 5

    def test_record_run_persists_to_file(self, runner, tmp_history):
        runner.record_run("skill-1", 85.0, 120.5, 90.0, 4, 5)
        assert tmp_history.exists()
        data = json.loads(tmp_history.read_text(encoding="utf-8"))
        assert "skill-1" in data
        assert len(data["skill-1"]) == 1

    def test_record_run_multiple_entries(self, runner):
        for i in range(5):
            runner.record_run("skill-1", 80.0 + i, 100.0 + i * 10, 85.0, 3, 5)
        hist = runner.get_history("skill-1")
        assert len(hist) == 5


class TestSkillsBenchRunnerGetHistory:
    def test_get_history_empty(self, runner):
        assert runner.get_history("no-skill") == []

    def test_get_history_respects_limit(self, runner):
        for i in range(15):
            runner.record_run("skill-1", 80.0, 100.0, 85.0, 3, 5)
        hist = runner.get_history("skill-1", limit=5)
        assert len(hist) == 5

    def test_get_history_returns_latest(self, runner):
        for i in range(10):
            runner.record_run("skill-1", float(i), 100.0, 85.0, 3, 5)
        hist = runner.get_history("skill-1", limit=3)
        assert hist[0]["score"] == 7.0
        assert hist[2]["score"] == 9.0


class TestSkillsBenchRunnerDetectRegression:
    def test_insufficient_data(self, runner):
        runner.record_run("skill-1", 80.0, 100.0, 85.0, 3, 5)
        result = runner.detect_regression("skill-1")
        assert result["regression_detected"] is False
        assert result["reason"] == "insufficient_data"

    def test_no_regression_stable(self, runner):
        for _ in range(6):
            runner.record_run("skill-1", 85.0, 100.0, 85.0, 3, 5)
        result = runner.detect_regression("skill-1")
        assert result["regression_detected"] is False
        assert result["score_trend"] == "stable"

    def test_score_regression_detected(self, runner):
        for i in range(3):
            runner.record_run("skill-1", 90.0, 100.0, 85.0, 3, 5)
        for i in range(3):
            runner.record_run("skill-1", 50.0, 100.0, 85.0, 3, 5)
        result = runner.detect_regression("skill-1")
        assert result["regression_detected"] is True
        assert result["score_trend"] == "declining"

    def test_latency_regression_detected(self, runner):
        for i in range(3):
            runner.record_run("skill-1", 85.0, 50.0, 85.0, 3, 5)
        for i in range(3):
            runner.record_run("skill-1", 85.0, 300.0, 85.0, 3, 5)
        result = runner.detect_regression("skill-1")
        assert result["regression_detected"] is True
        assert result["latency_trend"] == "increasing"

    def test_improving_score(self, runner):
        for i in range(3):
            runner.record_run("skill-1", 50.0, 100.0, 85.0, 3, 5)
        for i in range(3):
            runner.record_run("skill-1", 90.0, 100.0, 85.0, 3, 5)
        result = runner.detect_regression("skill-1")
        assert result["score_trend"] == "improving"


class TestSkillEfficacyCalibratorInit:
    def test_instantiation(self, calibrator):
        assert calibrator.runner is not None
        assert calibrator.bench_results == {}
        assert calibrator.PASS_THRESHOLD == 70.0
        assert calibrator.SUITE_NAME == "SkillsBench-Zephyr"


class TestSkillEfficacyCalibratorRunBenchmark:
    def test_run_benchmark_import_error(self, calibrator):
        with patch.dict("sys.modules", {"zephyr.autonomy_core.skills.skill_loader": None}):
            result = calibrator.run_benchmark("nonexistent-skill")
            assert result["skill_id"] == "nonexistent-skill"
            assert result["passed"] is False

    def test_run_benchmark_with_mock_loader(self, calibrator):
        mock_loader = MagicMock()
        mock_loader.progressive_load.return_value = {
            "l1": {
                "skill_id": "test-skill",
                "name": "Test Skill",
                "allowed_tools": ["Read"],
                "description": "desc",
                "version": "1.0",
                "model_hint": "gpt-4o",
            },
            "l2": "A" * 100,
            "token_count_l2": 200,
        }
        with patch("zephyr.autonomy_core.skills.skill_loader.SkillLoader", return_value=mock_loader):
            result = calibrator.run_benchmark("test-skill")
            assert result["skill_id"] == "test-skill"
            assert result["score"] > 0
            assert "results" in result

    def test_run_benchmark_empty_body(self, calibrator):
        mock_loader = MagicMock()
        mock_loader.progressive_load.return_value = {
            "l1": {"skill_id": "test-skill", "name": "Test"},
            "l2": "",
            "token_count_l2": 0,
        }
        with patch("zephyr.autonomy_core.skills.skill_loader.SkillLoader", return_value=mock_loader):
            result = calibrator.run_benchmark("test-skill")
            assert result["skill_id"] == "test-skill"


class TestSkillEfficacyCalibratorCalibrate:
    def test_calibrate_with_mock(self, calibrator):
        mock_loader = MagicMock()
        mock_loader.progressive_load.return_value = {
            "l1": {
                "skill_id": "test-skill",
                "name": "Test Skill",
                "allowed_tools": ["Read"],
                "description": "desc",
            },
            "l2": "A" * 100,
            "token_count_l2": 200,
        }
        with patch("zephyr.autonomy_core.skills.skill_loader.SkillLoader", return_value=mock_loader):
            result = calibrator.calibrate("test-skill", target_accuracy=80.0)
            assert result["skill_id"] == "test-skill"
            assert "current_accuracy" in result
            assert "target_accuracy" in result
            assert "gap" in result
            assert "calibrated" in result
            assert "suggestions" in result

    def test_calibrate_import_error(self, calibrator):
        with patch.dict("sys.modules", {"zephyr.autonomy_core.skills.skill_loader": None}):
            result = calibrator.calibrate("no-skill", target_accuracy=90.0)
            assert result["skill_id"] == "no-skill"
            assert result["calibrated"] is False
