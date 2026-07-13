# [A_test] module_id: SRC-TST-1078 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_gradual_poisoning_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_gradual_poisoning_detector.py
# [TTL] task_bound


from zephyr.feedback_loop.detectors.drift.gradual_poisoning_detector import (
    GradualPoisoningDetector,
    PoisoningSignal,
)


class TestPoisoningSignal:
    def test_default_instantiation(self):
        signal = PoisoningSignal()
        assert signal.short_term_mean == 0.0
        assert signal.long_term_mean == 0.0
        assert signal.cumulative_deviation == 0.0

    def test_custom_values(self):
        signal = PoisoningSignal(short_term_mean=5.0, long_term_mean=3.0, cumulative_deviation=2.0)
        assert signal.short_term_mean == 5.0
        assert signal.long_term_mean == 3.0
        assert signal.cumulative_deviation == 2.0

    def test_is_dataclass(self):
        signal = PoisoningSignal()
        assert hasattr(signal, "__dataclass_fields__")


class TestGradualPoisoningDetectorInstantiation:
    def test_default_instantiation(self):
        detector = GradualPoisoningDetector()
        assert detector.threshold == 3.0
        assert len(detector.short_window) == 0
        assert len(detector.long_window) == 0

    def test_custom_threshold(self):
        detector = GradualPoisoningDetector(threshold=5.0)
        assert detector.threshold == 5.0

    def test_is_dataclass(self):
        detector = GradualPoisoningDetector()
        assert hasattr(detector, "__dataclass_fields__")


class TestObserve:
    def test_single_observation(self):
        detector = GradualPoisoningDetector()
        signal = detector.observe(10.0)
        assert signal.short_term_mean == 10.0
        assert signal.long_term_mean == 10.0

    def test_multiple_observations(self):
        detector = GradualPoisoningDetector()
        detector.observe(10.0)
        detector.observe(12.0)
        signal = detector.observe(14.0)
        assert signal.short_term_mean > 0
        assert signal.long_term_mean > 0

    def test_returns_poisoning_signal(self):
        detector = GradualPoisoningDetector()
        signal = detector.observe(5.0)
        assert isinstance(signal, PoisoningSignal)

    def test_cumulative_deviation_computed(self):
        detector = GradualPoisoningDetector()
        for _ in range(50):
            detector.observe(10.0)
        for _ in range(50):
            detector.observe(20.0)
        signal = detector.observe(20.0)
        assert signal.cumulative_deviation > 0

    def test_short_window_maxlen(self):
        detector = GradualPoisoningDetector()
        for i in range(200):
            detector.observe(float(i))
        assert len(detector.short_window) <= 100

    def test_long_window_maxlen(self):
        detector = GradualPoisoningDetector()
        for i in range(2000):
            detector.observe(float(i))
        assert len(detector.long_window) <= 1000


class TestIsPoisoned:
    def test_insufficient_data_returns_false(self):
        detector = GradualPoisoningDetector()
        for i in range(50):
            detector.observe(10.0)
        assert detector.is_poisoned() is False

    def test_no_poisoning_returns_false(self):
        detector = GradualPoisoningDetector()
        for i in range(200):
            detector.observe(10.0)
        assert detector.is_poisoned() is False

    def test_poisoning_detected_with_drift(self):
        detector = GradualPoisoningDetector(threshold=1.0)
        for _ in range(200):
            detector.observe(10.0)
        for _ in range(200):
            detector.observe(50.0)
        assert detector.is_poisoned() is True

    def test_empty_detector_returns_false(self):
        detector = GradualPoisoningDetector()
        assert detector.is_poisoned() is False

    def test_exactly_100_long_window_not_poisoned(self):
        detector = GradualPoisoningDetector()
        for i in range(100):
            detector.observe(10.0)
        assert detector.is_poisoned() is False
