# [A_test] module_id: SRC-TST-1019 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_fle_performance_regression_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_fle_performance_regression_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.correlation.fle_performance_regression_detector import (
    FLEPerformanceRegressionDetector,
    PerformanceBaseline,
)


class TestPerformanceBaseline:
    def test_instantiation(self):
        baseline = PerformanceBaseline(
            latency_ms=100.0,
            throughput_per_sec=50.0,
            accuracy=0.95,
            cycle_count=10,
            timestamp=1000.0,
        )
        assert baseline.latency_ms == 100.0
        assert baseline.throughput_per_sec == 50.0
        assert baseline.accuracy == 0.95
        assert baseline.cycle_count == 10

    def test_is_dataclass(self):
        baseline = PerformanceBaseline(
            latency_ms=100.0,
            throughput_per_sec=50.0,
            accuracy=0.95,
            cycle_count=10,
            timestamp=1000.0,
        )
        assert hasattr(baseline, "__dataclass_fields__")


class TestFLEPerformanceRegressionDetectorInstantiation:
    def test_default_instantiation(self):
        detector = FLEPerformanceRegressionDetector()
        assert detector.baseline is None
        assert detector.current_metrics == []
        assert detector.max_history == 100
        assert detector.regression_threshold_latency == 0.3
        assert detector.regression_threshold_throughput == 0.2

    def test_custom_parameters(self):
        detector = FLEPerformanceRegressionDetector(
            regression_threshold_latency=0.5,
            regression_threshold_throughput=0.3,
        )
        assert detector.regression_threshold_latency == 0.5

    def test_is_dataclass(self):
        detector = FLEPerformanceRegressionDetector()
        assert hasattr(detector, "__dataclass_fields__")


class TestEstablishBaseline:
    def test_creates_baseline(self):
        detector = FLEPerformanceRegressionDetector()
        detector.establish_baseline(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95, cycle_count=10)
        assert detector.baseline is not None
        assert detector.baseline.latency_ms == 100.0
        assert detector.baseline.throughput_per_sec == 50.0
        assert detector.baseline.accuracy == 0.95
        assert detector.baseline.cycle_count == 10

    def test_overwrites_existing_baseline(self):
        detector = FLEPerformanceRegressionDetector()
        detector.establish_baseline(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95, cycle_count=10)
        detector.establish_baseline(latency_ms=200.0, throughput_per_sec=25.0, accuracy=0.90, cycle_count=20)
        assert detector.baseline.latency_ms == 200.0


class TestRecordMetrics:
    def test_record_appends_metric(self):
        detector = FLEPerformanceRegressionDetector()
        detector.record_metrics(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95)
        assert len(detector.current_metrics) == 1

    def test_record_multiple_metrics(self):
        detector = FLEPerformanceRegressionDetector()
        detector.record_metrics(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95)
        detector.record_metrics(latency_ms=110.0, throughput_per_sec=48.0, accuracy=0.94)
        assert len(detector.current_metrics) == 2

    def test_max_history_respected(self):
        detector = FLEPerformanceRegressionDetector(max_history=5)
        for i in range(10):
            detector.record_metrics(latency_ms=float(i), throughput_per_sec=50.0, accuracy=0.95)
        assert len(detector.current_metrics) == 5


class TestDetectRegression:
    def test_no_baseline(self):
        detector = FLEPerformanceRegressionDetector()
        detector.record_metrics(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95)
        result = detector.detect_regression()
        assert result["status"] == "no_baseline"
        assert result["regression_detected"] is False

    def test_no_current_metrics(self):
        detector = FLEPerformanceRegressionDetector()
        detector.establish_baseline(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95, cycle_count=10)
        result = detector.detect_regression()
        assert result["status"] == "no_baseline"
        assert result["regression_detected"] is False

    def test_no_regression(self):
        detector = FLEPerformanceRegressionDetector()
        detector.establish_baseline(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95, cycle_count=10)
        detector.record_metrics(latency_ms=105.0, throughput_per_sec=49.0, accuracy=0.95)
        result = detector.detect_regression()
        assert result["regression_detected"] is False
        assert result["recommendation"] == "CONTINUE"

    def test_latency_regression_warning(self):
        detector = FLEPerformanceRegressionDetector(regression_threshold_latency=0.3)
        detector.establish_baseline(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95, cycle_count=10)
        detector.record_metrics(latency_ms=140.0, throughput_per_sec=50.0, accuracy=0.95)
        result = detector.detect_regression()
        assert result["regression_detected"] is True
        assert "latency_increased" in result["regressions"]
        assert result["status"] == "warning"

    def test_throughput_regression_warning(self):
        detector = FLEPerformanceRegressionDetector(regression_threshold_throughput=0.2)
        detector.establish_baseline(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95, cycle_count=10)
        detector.record_metrics(latency_ms=100.0, throughput_per_sec=35.0, accuracy=0.95)
        result = detector.detect_regression()
        assert result["regression_detected"] is True
        assert "throughput_decreased" in result["regressions"]

    def test_critical_regression_both(self):
        detector = FLEPerformanceRegressionDetector(
            regression_threshold_latency=0.3,
            regression_threshold_throughput=0.2,
        )
        detector.establish_baseline(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95, cycle_count=10)
        detector.record_metrics(latency_ms=150.0, throughput_per_sec=30.0, accuracy=0.95)
        result = detector.detect_regression()
        assert result["status"] == "critical"
        assert result["recommendation"] == "ROLLBACK"
        assert len(result["regressions"]) == 2

    def test_result_contains_baseline_and_current(self):
        detector = FLEPerformanceRegressionDetector()
        detector.establish_baseline(latency_ms=100.0, throughput_per_sec=50.0, accuracy=0.95, cycle_count=10)
        detector.record_metrics(latency_ms=105.0, throughput_per_sec=49.0, accuracy=0.95)
        result = detector.detect_regression()
        assert "baseline_latency_ms" in result
        assert "current_avg_latency_ms" in result
        assert "latency_change_pct" in result
        assert "baseline_throughput" in result
        assert "current_avg_throughput" in result
        assert "throughput_change_pct" in result
