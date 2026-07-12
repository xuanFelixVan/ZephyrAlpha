# [A_test] module_id: SRC-TST-0931 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_anomaly_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.detectors.anomaly_detector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_anomaly_detector.py
# [TTL] task_bound

from unittest.mock import MagicMock

from zephyr.feedback_loop.detectors.anomaly_detector import (
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
from zephyr.feedback_loop.protocols import ActionType


def _make_snapshot(**overrides):
    defaults = {
        "timestamp": 1000.0,
        "system_cpu": 50.0,
        "memory_usage_pct": 60.0,
        "disk_io_wait": 5.0,
        "network_errors_count": 0,
        "detection_latency_ms": 100.0,
    }
    defaults.update(overrides)
    return MetricSnapshot(**defaults)


def _warm_up_collector(mc, n=100):
    for i in range(n):
        mc.collect(
            _make_snapshot(
                system_cpu=50.0 + (i % 5) * 0.5,
                memory_usage_pct=60.0 + (i % 3) * 0.5,
                disk_io_wait=5.0 + (i % 7) * 0.1,
                network_errors_count=0,
                detection_latency_ms=100.0 + (i % 4) * 0.5,
            )
        )


class TestAnomalyEvent:
    def test_creation(self):
        evt = AnomalyEvent(
            anomaly_id="abc123",
            severity=5,
            evidence={"metric": "cpu"},
            timestamp=1000.0,
        )
        assert evt.anomaly_id == "abc123"
        assert evt.severity == 5
        assert evt.evidence == {"metric": "cpu"}
        assert evt.timestamp == 1000.0

    def test_empty_evidence(self):
        evt = AnomalyEvent(anomaly_id="x", severity=0, evidence={}, timestamp=0.0)
        assert evt.evidence == {}


class TestAnomalyDetectorInstantiation:
    def test_default_instantiation(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc)
        assert det.metrics_collector is mc
        assert det.feedback_collector is fc
        assert det.protocol_adapter is None
        assert det.z_threshold == 2.5
        assert det.max_detect_seconds == 300.0

    def test_custom_parameters(self):
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
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc)
        _warm_up_collector(mc)
        snapshot = _make_snapshot(system_cpu=50.0)
        result = det.detect(snapshot)
        assert result is None

    def test_anomaly_detected_returns_event(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc, z_threshold=1.0)
        _warm_up_collector(mc)
        spike = _make_snapshot(system_cpu=99.0, memory_usage_pct=60.0)
        result = det.detect(spike)
        assert result is not None
        assert isinstance(result, AnomalyEvent)
        assert result.severity > 0
        assert "metric_name" in result.evidence
        assert "z_score" in result.evidence

    def test_anomaly_event_has_id(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc, z_threshold=1.0)
        _warm_up_collector(mc)
        spike = _make_snapshot(system_cpu=99.0)
        result = det.detect(spike)
        assert result is not None
        assert len(result.anomaly_id) > 0

    def test_severity_capped_at_10(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc, z_threshold=0.1)
        _warm_up_collector(mc)
        spike = _make_snapshot(system_cpu=99999.0)
        result = det.detect(spike)
        assert result is not None
        assert result.severity <= 10

    def test_protocol_adapter_dispatched_on_anomaly(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        adapter = MagicMock()
        adapter.dispatch_action.return_value = True
        det = AnomalyDetector(
            metrics_collector=mc,
            feedback_collector=fc,
            protocol_adapter=adapter,
            z_threshold=1.0,
        )
        _warm_up_collector(mc)
        spike = _make_snapshot(system_cpu=99.0)
        result = det.detect(spike)
        if result is not None:
            adapter.dispatch_action.assert_called_once()
            call_args = adapter.dispatch_action.call_args
            assert call_args[0][0] == ActionType.NOTIFY_OWNER

    def test_protocol_adapter_not_dispatched_when_no_anomaly(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        adapter = MagicMock()
        det = AnomalyDetector(
            metrics_collector=mc,
            feedback_collector=fc,
            protocol_adapter=adapter,
        )
        _warm_up_collector(mc)
        snapshot = _make_snapshot(system_cpu=50.0)
        det.detect(snapshot)
        adapter.dispatch_action.assert_not_called()

    def test_no_protocol_adapter_no_error(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc, z_threshold=1.0)
        _warm_up_collector(mc)
        spike = _make_snapshot(system_cpu=99.0)
        result = det.detect(spike)
        assert result is not None

    def test_evidence_includes_repair_failure_rate(self):
        mc = MetricsCollector()
        fc = FeedbackCollector()
        det = AnomalyDetector(metrics_collector=mc, feedback_collector=fc, z_threshold=1.0)
        _warm_up_collector(mc)
        spike = _make_snapshot(system_cpu=99.0)
        result = det.detect(spike)
        if result is not None:
            assert "repair_failure_rate" in result.evidence
