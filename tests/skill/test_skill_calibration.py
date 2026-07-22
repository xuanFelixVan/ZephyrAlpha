# [A_test] module_id: MOD-GOV_skill_calibration | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_calibration
# [INVARIANTS] drift = confidence - accuracy; calibrated iff |drift| < 0.1
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] calibrate returns dict with required keys
# [TESTS] tests/test_skill_calibration.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.autonomy_core.skills.skill_calibration import CalibrationEntry, SkillCalibration


class TestCalibrationEntry:
    def test_instantiation(self):
        entry = CalibrationEntry(confidence=0.9, actual_accuracy=0.8, timestamp=1000.0)
        assert entry.confidence == 0.9
        assert entry.actual_accuracy == 0.8
        assert entry.timestamp == 1000.0
        assert entry.drift == pytest.approx(0.1)

    def test_negative_drift(self):
        entry = CalibrationEntry(confidence=0.5, actual_accuracy=0.8, timestamp=1000.0)
        assert entry.drift == pytest.approx(-0.3)

    def test_zero_drift(self):
        entry = CalibrationEntry(confidence=0.7, actual_accuracy=0.7, timestamp=1000.0)
        assert entry.drift == pytest.approx(0.0)

    def test_to_dict(self):
        entry = CalibrationEntry(confidence=0.9, actual_accuracy=0.8, timestamp=1000.0)
        d = entry.to_dict()
        assert d["confidence"] == 0.9
        assert d["accuracy"] == 0.8
        assert d["drift"] == pytest.approx(0.1)
        assert d["timestamp"] == 1000.0


class TestSkillCalibrationCalibrate:
    def setup_method(self):
        SkillCalibration.clear_history("test_skill")

    def teardown_method(self):
        SkillCalibration.clear_history("test_skill")

    def test_calibrate_calibrated(self):
        result = SkillCalibration.calibrate("test_skill", 0.85, 0.82)
        assert result["skill_id"] == "test_skill"
        assert result["calibrated"] is True
        assert result["overconfident"] is False
        assert result["underconfident"] is False

    def test_calibrate_overconfident(self):
        result = SkillCalibration.calibrate("test_skill", 0.95, 0.7)
        assert result["overconfident"] is True
        assert result["drift"] > 0

    def test_calibrate_underconfident(self):
        result = SkillCalibration.calibrate("test_skill", 0.5, 0.7)
        assert result["underconfident"] is True
        assert result["drift"] < 0

    def test_calibrate_boundary_overconfidence(self):
        result = SkillCalibration.calibrate("test_skill", 0.85, 0.70)
        assert result["drift"] == pytest.approx(0.15)
        assert result["overconfident"] is True

    def test_calibrate_returns_required_keys(self):
        result = SkillCalibration.calibrate("test_skill", 0.8, 0.75)
        for key in ("skill_id", "confidence", "accuracy", "drift", "calibrated", "overconfident", "underconfident"):
            assert key in result

    def test_calibrate_zero_confidence(self):
        result = SkillCalibration.calibrate("test_skill", 0.0, 0.0)
        assert result["drift"] == pytest.approx(0.0)
        assert result["calibrated"] is True

    def test_calibrate_perfect_accuracy(self):
        result = SkillCalibration.calibrate("test_skill", 1.0, 1.0)
        assert result["drift"] == pytest.approx(0.0)
        assert result["calibrated"] is True

    def test_calibrate_extreme_overconfidence(self):
        result = SkillCalibration.calibrate("test_skill", 1.0, 0.0)
        assert result["drift"] == pytest.approx(1.0)
        assert result["overconfident"] is True


class TestSkillCalibrationDriftTrend:
    def setup_method(self):
        SkillCalibration.clear_history("trend_skill")

    def teardown_method(self):
        SkillCalibration.clear_history("trend_skill")

    def test_drift_trend_no_history(self):
        result = SkillCalibration.drift_trend("trend_skill")
        assert result["samples"] == 0
        assert result["avg_drift"] == 0.0

    def test_drift_trend_with_history(self):
        for i in range(5):
            SkillCalibration.calibrate("trend_skill", 0.8, 0.75)
        result = SkillCalibration.drift_trend("trend_skill")
        assert result["samples"] == 5
        assert result["avg_drift"] != 0.0

    def test_drift_trend_window(self):
        for i in range(15):
            SkillCalibration.calibrate("trend_skill", 0.8, 0.75)
        result = SkillCalibration.drift_trend("trend_skill", window=10)
        assert result["samples"] == 10

    def test_drift_trend_increasing_overconfidence(self):
        SkillCalibration.calibrate("trend_skill", 0.6, 0.5)
        SkillCalibration.calibrate("trend_skill", 0.7, 0.5)
        SkillCalibration.calibrate("trend_skill", 0.8, 0.5)
        result = SkillCalibration.drift_trend("trend_skill")
        assert result["trend"] == "increasing_overconfidence"

    def test_drift_trend_increasing_underconfidence(self):
        SkillCalibration.calibrate("trend_skill", 0.5, 0.6)
        SkillCalibration.calibrate("trend_skill", 0.4, 0.6)
        SkillCalibration.calibrate("trend_skill", 0.3, 0.6)
        result = SkillCalibration.drift_trend("trend_skill")
        assert result["trend"] == "increasing_underconfidence"

    def test_drift_trend_insufficient_data(self):
        SkillCalibration.calibrate("trend_skill", 0.8, 0.75)
        result = SkillCalibration.drift_trend("trend_skill")
        assert result["trend"] == "insufficient_data"

    def test_drift_trend_overconfident_ratio(self):
        for _ in range(5):
            SkillCalibration.calibrate("trend_skill", 0.95, 0.7)
        for _ in range(5):
            SkillCalibration.calibrate("trend_skill", 0.8, 0.75)
        result = SkillCalibration.drift_trend("trend_skill")
        assert 0.0 <= result["overconfident_ratio"] <= 1.0


class TestSkillCalibrationShouldRecalibrate:
    def setup_method(self):
        SkillCalibration.clear_history("recal_skill")

    def teardown_method(self):
        SkillCalibration.clear_history("recal_skill")

    def test_should_recalibrate_insufficient_samples(self):
        SkillCalibration.calibrate("recal_skill", 0.9, 0.7)
        result = SkillCalibration.should_recalibrate("recal_skill")
        assert result["should_recalibrate"] is False

    def test_should_recalibrate_overconfidence(self):
        for _ in range(8):
            SkillCalibration.calibrate("recal_skill", 0.95, 0.7)
        result = SkillCalibration.should_recalibrate("recal_skill")
        assert result["should_recalibrate"] is True
        assert "overconfidence" in result["reason"]

    def test_should_recalibrate_stable(self):
        for _ in range(8):
            SkillCalibration.calibrate("recal_skill", 0.8, 0.78)
        result = SkillCalibration.should_recalibrate("recal_skill")
        assert result["should_recalibrate"] is False

    def test_should_recalibrate_no_history(self):
        result = SkillCalibration.should_recalibrate("recal_skill")
        assert result["should_recalibrate"] is False
        assert result["reason"] == ""


class TestSkillCalibrationClearHistory:
    def setup_method(self):
        SkillCalibration.clear_history("clear_skill")

    def teardown_method(self):
        SkillCalibration.clear_history("clear_skill")

    def test_clear_specific_skill(self):
        SkillCalibration.calibrate("clear_skill", 0.8, 0.75)
        SkillCalibration.calibrate("other_skill", 0.8, 0.75)
        SkillCalibration.clear_history("clear_skill")
        result = SkillCalibration.drift_trend("clear_skill")
        assert result["samples"] == 0
        SkillCalibration.clear_history("other_skill")

    def test_clear_all_history(self):
        SkillCalibration.calibrate("clear_skill", 0.8, 0.75)
        SkillCalibration.calibrate("another_skill", 0.8, 0.75)
        SkillCalibration.clear_history()
        result = SkillCalibration.drift_trend("clear_skill")
        assert result["samples"] == 0
        result2 = SkillCalibration.drift_trend("another_skill")
        assert result2["samples"] == 0


class TestSkillCalibrationTrendDirection:
    def test_insufficient_data(self):
        assert SkillCalibration._trend_direction([0.1]) == "insufficient_data"

    def test_increasing_overconfidence_all_positive(self):
        assert SkillCalibration._trend_direction([0.1, 0.2, 0.3]) == "increasing_overconfidence"

    def test_increasing_underconfidence_all_negative(self):
        assert SkillCalibration._trend_direction([-0.1, -0.2, -0.3]) == "increasing_underconfidence"

    def test_stable_mixed(self):
        assert SkillCalibration._trend_direction([0.1, -0.1, 0.1]) == "stable"

    def test_ascending_sequence(self):
        assert SkillCalibration._trend_direction([-0.1, 0.0, 0.1]) == "increasing_overconfidence"

    def test_descending_sequence(self):
        assert SkillCalibration._trend_direction([0.1, 0.0, -0.1]) == "increasing_underconfidence"
