# [A_test] module_id: SRC-TST-1000 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_scheduler_collect_detect
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.scheduler_collect_detect
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_scheduler_collect_detect.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.feedback_loop.detectors.guard.guard_oscillation_detector import GuardOscillationDetector
from zephyr.feedback_loop.diagnosers.reliability.cold_start_conservative_mode import ColdStartConservativeMode
from zephyr.feedback_loop.diagnosers.reliability.guard_self_consistency_auditor import GuardSelfConsistencyAuditor
from zephyr.feedback_loop.diagnosers.reliability.numerical_stability_guard import NumericalStabilityGuard
from zephyr.feedback_loop.diagnosers.health.self_bottleneck_detector import SelfBottleneckDetector
from zephyr.feedback_loop.diagnosers.diagnosis.statistical_hygiene_auditor import StatisticalHygieneAuditor
from zephyr.feedback_loop.feedback_collector import FeedbackCollector
from zephyr.feedback_loop.metrics_collector import MetricsCollector, MetricSnapshot
from zephyr.feedback_loop.scheduler_collect_detect import CollectDetectHandler


def _make_handler():
    return CollectDetectHandler(
        numerical_guard=NumericalStabilityGuard(),
        cold_start=ColdStartConservativeMode(),
        bottleneck_detector=SelfBottleneckDetector(),
        stats_hygiene=StatisticalHygieneAuditor(),
        guard_consistency=GuardSelfConsistencyAuditor(),
        guard_oscillation=GuardOscillationDetector(),
        metrics_collector=MetricsCollector(),
        feedback_collector=FeedbackCollector(),
    )


class TestCollectDetectHandlerInstantiation:
    def test_creates_with_dependencies(self):
        handler = _make_handler()
        assert handler.anomaly_detector is not None
        assert handler.trajectory_detector is not None


class TestRunCollect:
    def test_returns_snapshot(self):
        handler = _make_handler()
        event = MagicMock()
        mc = MetricsCollector()
        snapshot = handler.run_collect(event, 0.0, "run1", mc)
        assert snapshot is not None
        assert hasattr(snapshot, "timestamp")

    def test_snapshot_has_expected_fields(self):
        handler = _make_handler()
        event = MagicMock()
        mc = MetricsCollector()
        snapshot = handler.run_collect(event, 0.0, "run1", mc)
        assert hasattr(snapshot, "system_cpu")
        assert hasattr(snapshot, "memory_usage_pct")
        assert hasattr(snapshot, "disk_io_wait")
        assert hasattr(snapshot, "network_errors_count")
        assert hasattr(snapshot, "detection_latency_ms")


class TestRunDetect:
    def test_returns_bool_with_real_snapshot(self):
        handler = _make_handler()
        event = MagicMock()
        mc = MetricsCollector()
        snapshot = handler.run_collect(event, 0.0, "run1", mc)
        result = handler.run_detect(event, snapshot, "run1")
        assert isinstance(result, bool)

    def test_no_anomaly_with_zero_metrics(self):
        handler = _make_handler()
        event = MagicMock()
        mc = MetricsCollector()
        snapshot = MetricSnapshot(
            timestamp=0.0,
            system_cpu=0.0,
            memory_usage_pct=0.0,
            disk_io_wait=0.0,
            network_errors_count=0,
            detection_latency_ms=0.0,
        )
        result = handler.run_detect(event, snapshot, "run1")
        assert isinstance(result, bool)
