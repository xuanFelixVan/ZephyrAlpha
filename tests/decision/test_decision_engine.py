# [A_test] module_id: SRC-TST-0715 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_decision_engine
# [INVARIANTS] test_coverage>=2_public_methods;boundary_tests_included
# [MODIFY-GUARD] sync_with_source_on_refactor
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest_exit_0_on_pass
# [TESTS] tests/test_decision_engine.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.feedback_loop.decision_engine import (
    _ANOMALY_TO_ACTION,
    _DEVIATION_THRESHOLDS,
    AnomalyReport,
    AnomalySeverity,
    DecisionEngine,
    ScheduleAdjustment,
    reflect_on_blueprint,
)
from zephyr.feedback_loop.protocols import ActionType


class TestAnomalySeverity:
    def test_values(self):
        assert AnomalySeverity.LOW.value == "LOW"
        assert AnomalySeverity.MEDIUM.value == "MEDIUM"
        assert AnomalySeverity.HIGH.value == "HIGH"
        assert AnomalySeverity.CRITICAL.value == "CRITICAL"

    def test_count(self):
        assert len(AnomalySeverity) == 4


class TestAnomalyReport:
    def test_construction(self):
        r = AnomalyReport(
            anomaly_type="drift",
            severity=AnomalySeverity.HIGH,
            metric_name="health",
            current_value=0.5,
            baseline_value=1.0,
            deviation_pct=50.0,
        )
        assert r.anomaly_type == "drift"
        assert r.severity == AnomalySeverity.HIGH
        assert r.context == {}

    def test_custom_context(self):
        r = AnomalyReport(
            anomaly_type="x",
            severity=AnomalySeverity.LOW,
            metric_name="m",
            current_value=1.0,
            baseline_value=1.0,
            deviation_pct=0.0,
            context={"key": "val"},
        )
        assert r.context["key"] == "val"


class TestScheduleAdjustment:
    def test_defaults(self):
        a = ScheduleAdjustment(action_type=ActionType.REPAIR)
        assert a.target_task_id == ""
        assert a.throttle_pct == 0.0
        assert a.anomaly_report is None


class TestDecisionEngine:
    def setup_method(self):
        self.engine = DecisionEngine()

    def _make_report(self, severity=AnomalySeverity.LOW, deviation=10.0):
        return AnomalyReport(
            anomaly_type="test",
            severity=severity,
            metric_name="m",
            current_value=1.0,
            baseline_value=1.0,
            deviation_pct=deviation,
        )

    def test_evaluate_low_no_throttle(self):
        r = self._make_report(AnomalySeverity.LOW, 10.0)
        adj = self.engine.evaluate_anomaly(r)
        assert adj.action_type == ActionType.REPAIR
        assert adj.throttle_pct == 0.0
        assert adj.anomaly_report is r

    def test_evaluate_high_has_throttle(self):
        r = self._make_report(AnomalySeverity.HIGH, 200.0)
        adj = self.engine.evaluate_anomaly(r)
        assert adj.action_type == ActionType.NOTIFY_OWNER
        assert adj.throttle_pct > 0.0
        assert adj.throttle_pct <= 50.0

    def test_evaluate_critical_throttle_capped(self):
        r = self._make_report(AnomalySeverity.CRITICAL, 999.0)
        adj = self.engine.evaluate_anomaly(r)
        assert adj.throttle_pct == 50.0

    def test_pending_without_adapter(self):
        r = self._make_report()
        self.engine.evaluate_anomaly(r)
        assert self.engine.pending_count == 1

    def test_flush_pending_no_adapter(self):
        r = self._make_report()
        self.engine.evaluate_anomaly(r)
        items = self.engine.flush_pending()
        assert len(items) == 1
        assert self.engine.pending_count == 0

    def test_with_adapter_dispatch(self):
        adapter = MagicMock()
        engine = DecisionEngine(adapter=adapter)
        r = self._make_report()
        engine.evaluate_anomaly(r)
        assert adapter.dispatch_action.called

    def test_adapter_failure_queues(self):
        adapter = MagicMock()
        adapter.dispatch_action.side_effect = RuntimeError("fail")
        engine = DecisionEngine(adapter=adapter)
        r = self._make_report()
        engine.evaluate_anomaly(r)
        assert engine.pending_count == 1

    def test_flush_with_adapter_success(self):
        adapter = MagicMock()
        engine = DecisionEngine(adapter=adapter)
        engine._pending = [ScheduleAdjustment(action_type=ActionType.REPAIR, reason="test")]
        engine.flush_pending()
        assert engine.pending_count == 0


class TestReflectOnBlueprint:
    def test_low_deviation(self):
        result = reflect_on_blueprint({"deviation_pct": 10.0})
        assert result["status"] == "reflected"
        assert result["anomaly_severity"] == "LOW"

    def test_critical_deviation(self):
        result = reflect_on_blueprint({"deviation_pct": 350.0})
        assert result["anomaly_severity"] == "CRITICAL"

    def test_default_values(self):
        result = reflect_on_blueprint({})
        assert result["status"] == "reflected"
        assert result["anomaly_severity"] == "LOW"

    def test_medium_threshold(self):
        result = reflect_on_blueprint({"deviation_pct": 120.0})
        assert result["anomaly_severity"] == "MEDIUM"

    def test_high_threshold(self):
        result = reflect_on_blueprint({"deviation_pct": 250.0})
        assert result["anomaly_severity"] == "HIGH"


class TestThresholds:
    def test_anomaly_to_action_mapping(self):
        assert _ANOMALY_TO_ACTION[AnomalySeverity.LOW] == ActionType.REPAIR
        assert _ANOMALY_TO_ACTION[AnomalySeverity.CRITICAL] == ActionType.NOTIFY_OWNER

    def test_deviation_thresholds_ordered(self):
        assert _DEVIATION_THRESHOLDS[AnomalySeverity.LOW] < _DEVIATION_THRESHOLDS[AnomalySeverity.MEDIUM]
        assert _DEVIATION_THRESHOLDS[AnomalySeverity.MEDIUM] < _DEVIATION_THRESHOLDS[AnomalySeverity.HIGH]
        assert _DEVIATION_THRESHOLDS[AnomalySeverity.HIGH] < _DEVIATION_THRESHOLDS[AnomalySeverity.CRITICAL]
