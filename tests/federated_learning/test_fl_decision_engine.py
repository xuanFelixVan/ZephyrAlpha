# [A_test] module_id: SRC-TST-0953 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_decision_engine
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.decision_engine
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_decision_engine.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.feedback_loop.decision_engine import (
    AnomalyReport,
    AnomalySeverity,
    DecisionEngine,
    reflect_on_blueprint,
)
from zephyr.feedback_loop.protocols import ActionType


class TestDecisionEngineInstantiation:
    def test_creates_without_adapter(self):
        engine = DecisionEngine()
        assert engine._adapter is None
        assert engine._pending == []

    def test_creates_with_adapter(self):
        adapter = MagicMock()
        engine = DecisionEngine(adapter=adapter)
        assert engine._adapter is adapter


class TestEvaluateAnomaly:
    def test_low_severity_produces_repair(self):
        engine = DecisionEngine()
        report = AnomalyReport(
            anomaly_type="spike",
            severity=AnomalySeverity.LOW,
            metric_name="cpu",
            current_value=80.0,
            baseline_value=50.0,
            deviation_pct=60.0,
        )
        result = engine.evaluate_anomaly(report)
        assert result.action_type == ActionType.REPAIR
        assert result.throttle_pct == 0.0

    def test_critical_severity_produces_notify_owner(self):
        engine = DecisionEngine()
        report = AnomalyReport(
            anomaly_type="outage",
            severity=AnomalySeverity.CRITICAL,
            metric_name="availability",
            current_value=0.0,
            baseline_value=99.9,
            deviation_pct=400.0,
        )
        result = engine.evaluate_anomaly(report)
        assert result.action_type == ActionType.NOTIFY_OWNER
        assert result.throttle_pct > 0.0

    def test_queues_when_no_adapter(self):
        engine = DecisionEngine()
        report = AnomalyReport(
            anomaly_type="spike",
            severity=AnomalySeverity.LOW,
            metric_name="cpu",
            current_value=80.0,
            baseline_value=50.0,
            deviation_pct=60.0,
        )
        engine.evaluate_anomaly(report)
        assert engine.pending_count == 1


class TestFlushPending:
    def test_flush_returns_items_when_no_adapter(self):
        engine = DecisionEngine()
        report = AnomalyReport(
            anomaly_type="spike",
            severity=AnomalySeverity.LOW,
            metric_name="cpu",
            current_value=80.0,
            baseline_value=50.0,
            deviation_pct=60.0,
        )
        engine.evaluate_anomaly(report)
        items = engine.flush_pending()
        assert len(items) == 1
        assert engine.pending_count == 0


class TestReflectOnBlueprint:
    def test_returns_reflected_status(self):
        result = reflect_on_blueprint({"deviation_pct": 100.0, "anomaly_type": "drift"})
        assert result["status"] == "reflected"
        assert "anomaly_severity" in result
        assert "action_type" in result

    def test_low_deviation(self):
        result = reflect_on_blueprint({"deviation_pct": 10.0})
        assert result["anomaly_severity"] == "LOW"
