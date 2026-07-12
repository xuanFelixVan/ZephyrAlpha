# [A_test] module_id: SRC-TST-0269 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_action_side_effect_cumulative_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_action_side_effect_cumulative_detector.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.detectors.action_side_effect_cumulative_detector import (
    ActionSideEffectCumulativeDetector,
)


class TestActionSideEffectCumulativeDetectorInstantiation:
    def test_default_construction(self):
        det = ActionSideEffectCumulativeDetector()
        assert det.baseline_metrics == {}
        assert det.cumulative_effects == {}
        assert det.max_effects_per_metric == 200
        assert det.drift_threshold == 0.15

    def test_custom_params(self):
        det = ActionSideEffectCumulativeDetector(
            max_effects_per_metric=50,
            drift_threshold=0.3,
        )
        assert det.max_effects_per_metric == 50
        assert det.drift_threshold == 0.3


class TestSetBaseline:
    def test_sets_baseline(self):
        det = ActionSideEffectCumulativeDetector()
        det.set_baseline({"cpu": 50.0, "mem": 80.0})
        assert det.baseline_metrics == {"cpu": 50.0, "mem": 80.0}

    def test_overwrites_existing(self):
        det = ActionSideEffectCumulativeDetector()
        det.set_baseline({"cpu": 50.0})
        det.set_baseline({"cpu": 60.0})
        assert det.baseline_metrics["cpu"] == 60.0

    def test_empty_baseline(self):
        det = ActionSideEffectCumulativeDetector()
        det.set_baseline({})
        assert det.baseline_metrics == {}


class TestRecordSideEffect:
    def test_creates_new_metric(self):
        det = ActionSideEffectCumulativeDetector()
        det.record_side_effect("cpu", 0.01)
        assert "cpu" in det.cumulative_effects
        assert det.cumulative_effects["cpu"] == [0.01]

    def test_appends_to_existing(self):
        det = ActionSideEffectCumulativeDetector()
        det.record_side_effect("cpu", 0.01)
        det.record_side_effect("cpu", 0.02)
        assert det.cumulative_effects["cpu"] == [0.01, 0.02]

    def test_truncates_at_max(self):
        det = ActionSideEffectCumulativeDetector(max_effects_per_metric=5)
        for i in range(8):
            det.record_side_effect("cpu", 0.01 * i)
        assert len(det.cumulative_effects["cpu"]) == 5

    def test_multiple_metrics(self):
        det = ActionSideEffectCumulativeDetector()
        det.record_side_effect("cpu", 0.01)
        det.record_side_effect("mem", 0.02)
        assert len(det.cumulative_effects) == 2


class TestDetectCumulativeDrift:
    def test_no_effects(self):
        det = ActionSideEffectCumulativeDetector()
        result = det.detect_cumulative_drift()
        assert result["drifted_metrics"] == []
        assert result["cumulative_drift_detected"] is False

    def test_no_drift_below_threshold(self):
        det = ActionSideEffectCumulativeDetector(drift_threshold=0.15)
        det.set_baseline({"cpu": 100.0})
        det.record_side_effect("cpu", 0.01)
        result = det.detect_cumulative_drift()
        assert result["cumulative_drift_detected"] is False

    def test_drift_detected(self):
        det = ActionSideEffectCumulativeDetector(drift_threshold=0.15)
        det.set_baseline({"cpu": 10.0})
        for _ in range(5):
            det.record_side_effect("cpu", 1.0)
        result = det.detect_cumulative_drift()
        assert result["cumulative_drift_detected"] is True
        assert "cpu" in result["drifted_metrics"]

    def test_zero_baseline(self):
        det = ActionSideEffectCumulativeDetector()
        det.set_baseline({"cpu": 0.0})
        det.record_side_effect("cpu", 0.5)
        result = det.detect_cumulative_drift()
        assert "cpu" in result["findings"]
        f = result["findings"]["cpu"]
        assert "cumulative_delta" in f
        assert "is_significant" in f

    def test_direction_increase(self):
        det = ActionSideEffectCumulativeDetector(drift_threshold=0.15)
        det.set_baseline({"cpu": 10.0})
        det.record_side_effect("cpu", 5.0)
        result = det.detect_cumulative_drift()
        assert result["findings"]["cpu"]["direction"] == "increase"

    def test_direction_decrease(self):
        det = ActionSideEffectCumulativeDetector(drift_threshold=0.15)
        det.set_baseline({"cpu": 10.0})
        det.record_side_effect("cpu", -5.0)
        result = det.detect_cumulative_drift()
        assert result["findings"]["cpu"]["direction"] == "decrease"


class TestGetTotalCumulativeEffects:
    def test_empty(self):
        det = ActionSideEffectCumulativeDetector()
        assert det.get_total_cumulative_effects() == {}

    def test_sums_effects(self):
        det = ActionSideEffectCumulativeDetector()
        det.record_side_effect("cpu", 0.1)
        det.record_side_effect("cpu", 0.2)
        det.record_side_effect("mem", -0.05)
        totals = det.get_total_cumulative_effects()
        assert totals["cpu"] == pytest.approx(0.3)
        assert totals["mem"] == pytest.approx(-0.05)
