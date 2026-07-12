# [A_test] module_id: SRC-TST-0830 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_emergent_behavior_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_emergent_behavior_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.emergent_behavior_detector import (
    EmergenceState,
    EmergentBehaviorDetector,
)


class TestEmergenceState:
    def test_enum_values(self):
        assert EmergenceState.STABLE.value == "STABLE"
        assert EmergenceState.CORRELATING.value == "CORRELATING"
        assert EmergenceState.CRITICAL.value == "CRITICAL"
        assert EmergenceState.HYSTERETIC.value == "HYSTERETIC"


class TestEmergentBehaviorDetectorInstantiation:
    def test_default_instantiation(self):
        detector = EmergentBehaviorDetector()
        assert detector.correlation_threshold == 0.70
        assert detector.entropy_drop_threshold == 0.30
        assert detector.hysteresis_threshold == 0.15
        assert detector.window_size == 50
        assert detector.state == EmergenceState.STABLE

    def test_custom_parameters(self):
        detector = EmergentBehaviorDetector(correlation_threshold=0.9, window_size=100)
        assert detector.correlation_threshold == 0.9
        assert detector.window_size == 100

    def test_is_dataclass(self):
        detector = EmergentBehaviorDetector()
        assert hasattr(detector, "__dataclass_fields__")


class TestRecordMetrics:
    def test_record_single_metric(self):
        detector = EmergentBehaviorDetector()
        detector.record_metrics({"cpu": 80.0})
        assert "cpu" in detector.metric_history
        assert len(detector.metric_history["cpu"]) == 1

    def test_record_multiple_metrics(self):
        detector = EmergentBehaviorDetector()
        detector.record_metrics({"cpu": 80.0, "mem": 60.0})
        assert len(detector.metric_history) == 2

    def test_record_appends_to_history(self):
        detector = EmergentBehaviorDetector()
        detector.record_metrics({"cpu": 80.0})
        detector.record_metrics({"cpu": 85.0})
        assert len(detector.metric_history["cpu"]) == 2

    def test_window_size_respected(self):
        detector = EmergentBehaviorDetector(window_size=5)
        for i in range(10):
            detector.record_metrics({"cpu": float(i)})
        assert len(detector.metric_history["cpu"]) == 5

    def test_empty_metrics_dict(self):
        detector = EmergentBehaviorDetector()
        detector.record_metrics({})
        assert len(detector.metric_history) == 0


class TestComputePairwiseCorrelations:
    def test_insufficient_data_returns_empty(self):
        detector = EmergentBehaviorDetector()
        detector.record_metrics({"a": 1.0})
        detector.record_metrics({"b": 2.0})
        correlations = detector.compute_pairwise_correlations()
        assert correlations == {}

    def test_sufficient_data_returns_correlation(self):
        detector = EmergentBehaviorDetector()
        for i in range(10):
            detector.record_metrics({"a": float(i), "b": float(i) * 2.0})
        correlations = detector.compute_pairwise_correlations()
        assert "a+b" in correlations

    def test_single_metric_no_pairs(self):
        detector = EmergentBehaviorDetector()
        for i in range(10):
            detector.record_metrics({"a": float(i)})
        correlations = detector.compute_pairwise_correlations()
        assert len(correlations) == 0

    def test_perfect_positive_correlation(self):
        detector = EmergentBehaviorDetector()
        for i in range(10):
            detector.record_metrics({"a": float(i), "b": float(i)})
        correlations = detector.compute_pairwise_correlations()
        assert correlations["a+b"] > 0.99


class TestDetectEmergence:
    def test_stable_with_no_data(self):
        detector = EmergentBehaviorDetector()
        result = detector.detect_emergence()
        assert result["state"] == EmergenceState.STABLE.value
        assert result["high_correlation_pairs"] == 0

    def test_correlating_state(self):
        detector = EmergentBehaviorDetector(correlation_threshold=0.5)
        for i in range(10):
            v = float(i)
            detector.record_metrics({"a": v, "b": v * 2.0})
        result = detector.detect_emergence()
        assert result["state"] in (
            EmergenceState.CORRELATING.value,
            EmergenceState.CRITICAL.value,
        )

    def test_recommendation_in_result(self):
        detector = EmergentBehaviorDetector()
        result = detector.detect_emergence()
        assert "recommendation" in result

    def test_emergence_events_recorded_on_state_change(self):
        detector = EmergentBehaviorDetector(correlation_threshold=0.5)
        detector.record_metrics({"a": 1.0, "b": 2.0})
        for i in range(10):
            v = float(i)
            detector.record_metrics({"a": v, "b": v * 2.0})
        detector.detect_emergence()
        if detector.state != EmergenceState.STABLE:
            assert len(detector.emergence_events) >= 1


class TestSetPreStressBaseline:
    def test_sets_baseline(self):
        detector = EmergentBehaviorDetector()
        detector.set_pre_stress_baseline({"cpu": 50.0, "mem": 40.0})
        assert detector.pre_stress_baseline is not None
        assert detector.pre_stress_baseline["cpu"] == 50.0

    def test_baseline_copies_values(self):
        detector = EmergentBehaviorDetector()
        metrics = {"cpu": 50.0}
        detector.set_pre_stress_baseline(metrics)
        metrics["cpu"] = 99.0
        assert detector.pre_stress_baseline["cpu"] == 50.0
