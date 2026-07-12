# [A_test] module_id: SRC-TST-1529 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_scheduler_collect_detect
# [INVARIANTS] CollectDetectHandler.run_collect/detect/diagnose return bool (should_early_return)
# [MODIFY-GUARD] none
# [CONSUMERS] CI pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exceptions on assertion failure
# [TESTS] tests/test_scheduler_collect_detect.py
# [TTL] task_bound

import time
from unittest.mock import MagicMock

from zephyr.feedback_loop.detectors.guard_oscillation_detector import GuardOscillationDetector
from zephyr.feedback_loop.diagnosers.cold_start_conservative_mode import ColdStartConservativeMode
from zephyr.feedback_loop.diagnosers.guard_self_consistency_auditor import GuardSelfConsistencyAuditor
from zephyr.feedback_loop.diagnosers.numerical_stability_guard import NumericalStabilityGuard
from zephyr.feedback_loop.diagnosers.self_bottleneck_detector import SelfBottleneckDetector
from zephyr.feedback_loop.diagnosers.statistical_hygiene_auditor import StatisticalHygieneAuditor
from zephyr.feedback_loop.feedback_collector import FeedbackCollector
from zephyr.feedback_loop.metrics_collector import MetricsCollector
from zephyr.feedback_loop.scheduler_collect_detect import CollectDetectHandler


def make_handler():
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


class TestCollectDetectHandlerInit:
    def test_instantiation(self):
        handler = make_handler()
        assert handler.anomaly_detector is not None
        assert handler.diagnosis_engine is not None
        assert handler.flapping_detector is not None


class TestRunCollect:
    def test_returns_snapshot(self):
        handler = make_handler()
        event = MagicMock()
        mc = MagicMock()
        now = time.time()
        snapshot = handler.run_collect(event, now, "run1", mc)
        assert snapshot is not None
        assert snapshot.timestamp == now

    def test_metrics_collector_called(self):
        handler = make_handler()
        event = MagicMock()
        mc = MagicMock()
        now = time.time()
        handler.run_collect(event, now, "run1", mc)
        mc.collect.assert_called_once()

    def test_event_snapshot_set(self):
        handler = make_handler()
        event = MagicMock()
        mc = MagicMock()
        now = time.time()
        handler.run_collect(event, now, "run1", mc)
        assert event.snapshot is not None


class TestRunDetect:
    def test_no_anomaly_returns_true(self):
        handler = make_handler()
        handler.anomaly_detector = MagicMock()
        handler.anomaly_detector.detect.return_value = None
        event = MagicMock()
        snapshot = MagicMock()
        result = handler.run_detect(event, snapshot, "run1")
        assert result is True

    def test_anomaly_not_flapping_returns_false(self):
        handler = make_handler()
        handler.anomaly_detector = MagicMock()
        mock_anomaly = MagicMock()
        mock_anomaly.anomaly_id = "a1"
        handler.anomaly_detector.detect.return_value = mock_anomaly
        handler.flapping_detector = MagicMock()
        handler.flapping_detector.record_state_change.return_value = {"suppressed": False}
        event = MagicMock()
        snapshot = MagicMock()
        result = handler.run_detect(event, snapshot, "run1")
        assert result is False
        assert event.anomaly is mock_anomaly

    def test_flapping_suppressed_returns_true(self):
        handler = make_handler()
        handler.anomaly_detector = MagicMock()
        mock_anomaly = MagicMock()
        mock_anomaly.anomaly_id = "a1"
        handler.anomaly_detector.detect.return_value = mock_anomaly
        handler.flapping_detector = MagicMock()
        handler.flapping_detector.record_state_change.return_value = {"suppressed": True}
        event = MagicMock()
        snapshot = MagicMock()
        result = handler.run_detect(event, snapshot, "run1")
        assert result is True


class TestRunDiagnose:
    def test_hygiene_violation_returns_true(self):
        handler = make_handler()
        handler.stats_hygiene = MagicMock()
        handler.stats_hygiene.check_sample_size.return_value = {"violation": True}
        event = MagicMock()
        event.anomaly = MagicMock()
        event.anomaly.anomaly_id = "a1"
        event.anomaly.evidence = {}
        mc = MagicMock()
        mc.baseline = MagicMock()
        mc.baseline.total_samples = 5
        result = handler.run_diagnose(event, mc)
        assert result is True

    def test_delay_suppress_returns_true(self):
        handler = make_handler()
        handler.stats_hygiene = MagicMock()
        handler.stats_hygiene.check_sample_size.return_value = {"violation": False}
        handler.delay_compensator = MagicMock()
        handler.delay_compensator.should_suppress.return_value = {"suppress": True, "remaining_seconds": 30}
        event = MagicMock()
        event.anomaly = MagicMock()
        event.anomaly.anomaly_id = "a1"
        event.anomaly.evidence = {"metric_name": "cpu"}
        mc = MagicMock()
        mc.baseline = MagicMock()
        mc.baseline.total_samples = 100
        result = handler.run_diagnose(event, mc)
        assert result is True

    def test_normal_diagnosis_returns_false(self):
        handler = make_handler()
        handler.stats_hygiene = MagicMock()
        handler.stats_hygiene.check_sample_size.return_value = {"violation": False}
        handler.delay_compensator = MagicMock()
        handler.delay_compensator.should_suppress.return_value = {"suppress": False}
        handler.diagnosis_engine = MagicMock()
        handler.diagnosis_engine.diagnose.return_value = MagicMock()
        handler.guard_oscillation = MagicMock()
        event = MagicMock()
        event.anomaly = MagicMock()
        event.anomaly.anomaly_id = "a1"
        event.anomaly.evidence = {"metric_name": "cpu"}
        mc = MagicMock()
        mc.baseline = MagicMock()
        mc.baseline.total_samples = 100
        result = handler.run_diagnose(event, mc)
        assert result is False
        assert event.diagnosis is not None
