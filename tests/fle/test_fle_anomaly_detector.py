# [A_test] module_id: SRC-TST-1011 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_anomaly_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_fle_anomaly_detector.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.feedback_loop.detectors.anomaly.anomaly_detector import (
    AnomalyDetector,
    AnomalyEvent,
)
from zephyr.feedback_loop.feedback_collector import (
    FeedbackCollector,
)
from zephyr.feedback_loop.metrics_collector import (
    MetricsCollector,
    MetricSnapshot,
)
from zephyr.feedback_loop.protocols import ActionType, FeedbackProtocolAdapter


def _make_snapshot(
    timestamp: float = 1.0,
    system_cpu: float = 50.0,
    memory_usage_pct: float = 60.0,
    disk_io_wait: float = 5.0,
    network_errors_count: int = 0,
    detection_latency_ms: float = 100.0,
) -> MetricSnapshot:
    return MetricSnapshot(
        timestamp=timestamp,
        system_cpu=system_cpu,
        memory_usage_pct=memory_usage_pct,
        disk_io_wait=disk_io_wait,
        network_errors_count=network_errors_count,
        detection_latency_ms=detection_latency_ms,
    )


class TestAnomalyEvent:
    def test_construction(self):
        ev = AnomalyEvent(
            anomaly_id="abc12345",
            severity=5,
            evidence={"metric_name": "cpu"},
            timestamp=1.0,
        )
        assert ev.anomaly_id == "abc12345"
        assert ev.severity == 5
        assert ev.evidence["metric_name"] == "cpu"


class TestAnomalyDetectorInstantiation:
    def test_default_construction(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc)
        assert det.z_threshold == 2.5
        assert det.max_detect_seconds == 300.0
        assert det.protocol_adapter is None

    def test_custom_params(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(
            metrics_collector=mc,
            feedback_collector=fc,
            z_threshold=3.0,
            max_detect_seconds=600.0,
        )
        assert det.z_threshold == 3.0
        assert det.max_detect_seconds == 600.0


class TestDetect:
    def test_no_anomaly_returns_none(self):
        mc = MagicMock(spec=MetricsCollector)
        mc.collect.return_value = {
            "snapshot": _make_snapshot(),
            "z_scores": {"system_cpu": 0.5, "memory_usage_pct": 0.3},
            "anomaly_triggered": False,
        }
        mc.baseline = MagicMock()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc)
        snapshot = _make_snapshot()
        result = det.detect(snapshot)
        assert result is None

    def test_anomaly_returns_event(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc, z_threshold=0.01)
        for i in range(20):
            mc.collect(_make_snapshot(system_cpu=50.0, timestamp=float(i)))
        anomalous = _make_snapshot(system_cpu=999.0, timestamp=21.0)
        result = det.detect(anomalous)
        assert result is not None
        assert isinstance(result, AnomalyEvent)
        assert result.severity > 0

    def test_event_evidence_fields(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc, z_threshold=0.01)
        for i in range(20):
            mc.collect(_make_snapshot(system_cpu=50.0, timestamp=float(i)))
        anomalous = _make_snapshot(system_cpu=999.0, timestamp=21.0)
        result = det.detect(anomalous)
        if result is not None:
            assert "metric_name" in result.evidence
            assert "z_score" in result.evidence
            assert "repair_failure_rate" in result.evidence

    def test_protocol_adapter_dispatched(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        adapter = MagicMock(spec=FeedbackProtocolAdapter)
        adapter.dispatch_action.return_value = True
        det = AnomalyDetector(
            metrics_collector=mc,
            feedback_collector=fc,
            protocol_adapter=adapter,
            z_threshold=0.01,
        )
        for i in range(20):
            mc.collect(_make_snapshot(system_cpu=50.0, timestamp=float(i)))
        anomalous = _make_snapshot(system_cpu=999.0, timestamp=21.0)
        result = det.detect(anomalous)
        if result is not None and result.severity > 0:
            adapter.dispatch_action.assert_called_once()
            call_args = adapter.dispatch_action.call_args
            assert call_args[0][0] == ActionType.NOTIFY_OWNER

    def test_protocol_adapter_not_dispatched_when_no_anomaly(self):
        mc = MagicMock(spec=MetricsCollector)
        mc.collect.return_value = {
            "snapshot": _make_snapshot(),
            "z_scores": {"system_cpu": 0.5, "memory_usage_pct": 0.3},
            "anomaly_triggered": False,
        }
        mc.baseline = MagicMock()
        fc = FeedbackCollector()
        adapter = MagicMock(spec=FeedbackProtocolAdapter)
        det = AnomalyDetector(
            metrics_collector=mc,
            feedback_collector=fc,
            protocol_adapter=adapter,
        )
        snapshot = _make_snapshot()
        det.detect(snapshot)
        adapter.dispatch_action.assert_not_called()

    def test_severity_capped_at_10(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc, z_threshold=0.001)
        for i in range(20):
            mc.collect(_make_snapshot(system_cpu=50.0, timestamp=float(i)))
        anomalous = _make_snapshot(system_cpu=99999.0, timestamp=21.0)
        result = det.detect(anomalous)
        if result is not None:
            assert result.severity <= 10
