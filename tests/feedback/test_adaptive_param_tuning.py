# [A_test] module_id: SRC-TST-0271 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_adaptive_param_tuning
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.cognitive.adaptive_param_tuning
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_adaptive_param_tuning.py
# [TTL] task_bound

from zephyr.feedback_loop.diagnosers.cognitive.adaptive_param_tuning import (
    AdaptiveParamTuning,
    TuningMode,
)


class TestTuningMode:
    def test_locked_value(self):
        assert TuningMode.LOCKED == "LOCKED"

    def test_adaptive_value(self):
        assert TuningMode.ADAPTIVE == "ADAPTIVE"

    def test_aggressive_value(self):
        assert TuningMode.AGGRESSIVE == "AGGRESSIVE"

    def test_is_str_enum(self):
        assert isinstance(TuningMode.LOCKED, str)


class TestAdaptiveParamTuning:
    def test_instantiation_default(self):
        apt = AdaptiveParamTuning()
        assert apt.alpha == 0.3
        assert apt.false_positive_tolerance == 0.05
        assert apt.false_negative_tolerance == 0.02
        assert apt.step_size == 0.1
        assert apt.min_threshold == 0.01
        assert apt.max_threshold == 10.0
        assert apt.mode == TuningMode.ADAPTIVE
        assert apt.current_threshold == 1.0
        assert apt.ewma_fp == 0.0
        assert apt.ewma_fn == 0.0
        assert apt.adjustment_history == []

    def test_instantiation_custom(self):
        apt = AdaptiveParamTuning(alpha=0.5, current_threshold=2.0)
        assert apt.alpha == 0.5
        assert apt.current_threshold == 2.0

    def test_observe_true_positive(self):
        apt = AdaptiveParamTuning()
        result = apt.observe(was_anomaly=True, was_true_positive=True)
        assert apt.ewma_fp == 0.0
        assert apt.ewma_fn == 0.0
        assert isinstance(result, float)

    def test_observe_false_positive_increases_threshold(self):
        apt = AdaptiveParamTuning(current_threshold=1.0)
        for _ in range(20):
            apt.observe(was_anomaly=False, was_true_positive=False)
        assert apt.current_threshold > 1.0

    def test_observe_false_negative_decreases_threshold(self):
        apt = AdaptiveParamTuning(current_threshold=2.0)
        for _ in range(20):
            apt.observe(was_anomaly=True, was_true_positive=False)
        assert apt.current_threshold < 2.0

    def test_observe_locked_mode_no_change(self):
        apt = AdaptiveParamTuning(current_threshold=1.0, mode=TuningMode.LOCKED)
        for _ in range(20):
            apt.observe(was_anomaly=False, was_true_positive=False)
        assert apt.current_threshold == 1.0

    def test_observe_respects_min_threshold(self):
        apt = AdaptiveParamTuning(current_threshold=0.02, min_threshold=0.01)
        for _ in range(50):
            apt.observe(was_anomaly=True, was_true_positive=False)
        assert apt.current_threshold >= apt.min_threshold

    def test_observe_respects_max_threshold(self):
        apt = AdaptiveParamTuning(current_threshold=9.9, max_threshold=10.0)
        for _ in range(50):
            apt.observe(was_anomaly=False, was_true_positive=False)
        assert apt.current_threshold <= apt.max_threshold

    def test_observe_records_history(self):
        apt = AdaptiveParamTuning()
        apt.observe(was_anomaly=True, was_true_positive=True)
        assert len(apt.adjustment_history) == 1
        assert "fp" in apt.adjustment_history[0]
        assert "fn" in apt.adjustment_history[0]
        assert "threshold" in apt.adjustment_history[0]

    def test_observe_history_truncation(self):
        apt = AdaptiveParamTuning()
        for _ in range(120):
            apt.observe(was_anomaly=True, was_true_positive=True)
        assert len(apt.adjustment_history) <= 100

    def test_lock(self):
        apt = AdaptiveParamTuning(mode=TuningMode.ADAPTIVE)
        apt.lock()
        assert apt.mode == TuningMode.LOCKED

    def test_unlock(self):
        apt = AdaptiveParamTuning(mode=TuningMode.LOCKED)
        apt.unlock()
        assert apt.mode == TuningMode.ADAPTIVE

    def test_lock_unlock_cycle(self):
        apt = AdaptiveParamTuning()
        apt.lock()
        assert apt.mode == TuningMode.LOCKED
        apt.unlock()
        assert apt.mode == TuningMode.ADAPTIVE

    def test_observe_returns_float(self):
        apt = AdaptiveParamTuning()
        result = apt.observe(was_anomaly=True, was_true_positive=True)
        assert isinstance(result, float)

    def test_ewma_fp_converges_on_false_positives(self):
        apt = AdaptiveParamTuning(alpha=0.5)
        for _ in range(30):
            apt.observe(was_anomaly=False, was_true_positive=False)
        assert apt.ewma_fp > 0.0

    def test_ewma_fn_converges_on_false_negatives(self):
        apt = AdaptiveParamTuning(alpha=0.5)
        for _ in range(30):
            apt.observe(was_anomaly=True, was_true_positive=False)
        assert apt.ewma_fn > 0.0
