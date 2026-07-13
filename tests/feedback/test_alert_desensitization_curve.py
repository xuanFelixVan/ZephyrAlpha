# [A_test] module_id: SRC-TST-0304 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_alert_desensitization_curve
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_alert_desensitization_curve.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.detectors.guard.alert_desensitization_curve import (
    AlertDesensitizationCurve,
)


class TestAlertDesensitizationCurveInstantiation:
    def test_default_construction(self):
        curve = AlertDesensitizationCurve()
        assert curve.decay_lambda == 0.1
        assert curve.threshold == 0.5
        assert curve.alert_exposures == {}
        assert curve.response_history == {}

    def test_custom_params(self):
        curve = AlertDesensitizationCurve(decay_lambda=0.2, threshold=0.3)
        assert curve.decay_lambda == 0.2
        assert curve.threshold == 0.3


class TestRecordExposure:
    def test_first_exposure(self):
        curve = AlertDesensitizationCurve()
        result = curve.record_exposure("disk_full", True)
        assert curve.alert_exposures["disk_full"] == 1
        assert isinstance(result, float)

    def test_multiple_exposures(self):
        curve = AlertDesensitizationCurve()
        curve.record_exposure("disk_full", True)
        curve.record_exposure("disk_full", False)
        assert curve.alert_exposures["disk_full"] == 2

    def test_response_history_truncated(self):
        curve = AlertDesensitizationCurve()
        for i in range(55):
            curve.record_exposure("disk_full", i % 2 == 0)
        assert len(curve.response_history["disk_full"]) <= 50

    def test_returns_desensitization_value(self):
        curve = AlertDesensitizationCurve()
        val = curve.record_exposure("disk_full", True)
        assert 0.0 <= val <= 1.0


class TestGetDesensitization:
    def test_zero_exposures(self):
        curve = AlertDesensitizationCurve()
        val = curve.get_desensitization("unknown_alert")
        assert val == 1.0

    def test_single_exposure(self):
        curve = AlertDesensitizationCurve()
        curve.record_exposure("disk_full", True)
        val = curve.get_desensitization("disk_full")
        assert val == pytest.approx(0.1)

    def test_decreasing_with_more_exposures(self):
        curve = AlertDesensitizationCurve()
        curve.record_exposure("disk_full", True)
        val1 = curve.get_desensitization("disk_full")
        curve.record_exposure("disk_full", True)
        val2 = curve.get_desensitization("disk_full")
        assert val2 < val1

    def test_clamped_to_zero(self):
        curve = AlertDesensitizationCurve()
        for _ in range(100):
            curve.record_exposure("disk_full", True)
        val = curve.get_desensitization("disk_full")
        assert val >= 0.0


class TestGetResponseRate:
    def test_no_history(self):
        curve = AlertDesensitizationCurve()
        assert curve.get_response_rate("unknown") == 1.0

    def test_all_responded(self):
        curve = AlertDesensitizationCurve()
        for _ in range(5):
            curve.record_exposure("disk_full", True)
        assert curve.get_response_rate("disk_full") == 1.0

    def test_none_responded(self):
        curve = AlertDesensitizationCurve()
        for _ in range(5):
            curve.record_exposure("disk_full", False)
        assert curve.get_response_rate("disk_full") == 0.0

    def test_mixed_response(self):
        curve = AlertDesensitizationCurve()
        curve.record_exposure("disk_full", True)
        curve.record_exposure("disk_full", False)
        assert curve.get_response_rate("disk_full") == pytest.approx(0.5)


class TestNeedsEscalation:
    def test_no_escalation_needed_with_slow_decay(self):
        curve = AlertDesensitizationCurve(decay_lambda=0.9, threshold=0.5)
        curve.record_exposure("disk_full", True)
        assert curve.needs_escalation("disk_full") is False

    def test_escalation_needed(self):
        curve = AlertDesensitizationCurve()
        for _ in range(20):
            curve.record_exposure("disk_full", True)
        assert curve.needs_escalation("disk_full") is True

    def test_unknown_alert_no_escalation(self):
        curve = AlertDesensitizationCurve()
        assert curve.needs_escalation("unknown") is False


class TestIsDesensitized:
    def test_none_desensitized_with_slow_decay(self):
        curve = AlertDesensitizationCurve(decay_lambda=0.9, threshold=0.5)
        curve.record_exposure("disk_full", True)
        assert curve.is_desensitized() == []

    def test_desensitized_alerts(self):
        curve = AlertDesensitizationCurve()
        for _ in range(20):
            curve.record_exposure("disk_full", True)
        result = curve.is_desensitized()
        assert "disk_full" in result
