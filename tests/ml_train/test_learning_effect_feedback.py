# [BLUEPRINT] MOD-ML-009 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [A_test] module_id: MOD-ML_test_learning_effect_feedback | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.ml_train.test_learning_effect_feedback
# [TESTS] src/zephyr/ml_train/learning_effect_feedback.py
# [TTL] task_bound
"""MOD-ML-009 学习效果反馈回喂 toy 断言。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.learning_effect_feedback import (
    FeedbackSignalError,
    LearningEffectFeedback,
)


def _paired(n: int = 60, ic: float = 0.8):
    rng = np.random.default_rng(5)
    pred = rng.normal(size=n)
    actual = ic * pred + np.sqrt(max(1e-9, 1 - ic**2)) * rng.normal(size=n)
    return pred, actual


class TestEffectComputation:
    def test_compute_effect_ic_and_decay(self):
        fb = LearningEffectFeedback()
        pred, actual = _paired()
        eff = fb.compute_effect("ML-DENSITY-001", predictions=pred, actuals=actual, baseline_ic=0.9)
        assert 0.0 < eff["ic"] < 1.0
        assert eff["ic_decay"] == pytest.approx(0.9 - eff["ic"], abs=1e-9)

    def test_length_mismatch_raises(self):
        fb = LearningEffectFeedback()
        with pytest.raises(FeedbackSignalError) as exc:
            fb.compute_effect("m1", predictions=np.zeros(5), actuals=np.zeros(6), baseline_ic=0.0)
        assert exc.value.error_code == "ZA-MLT-0008"

    def test_too_few_pairs_raises(self):
        fb = LearningEffectFeedback(min_pairs=10)
        with pytest.raises(FeedbackSignalError, match="样本对不足"):
            fb.compute_effect("m1", predictions=np.zeros(5), actuals=np.zeros(5), baseline_ic=0.0)


class TestFeedbackLoop:
    def test_feedback_recommends_retrain_on_decay(self):
        """IC 衰减超阈值 → 回喂 retrain 信号（只产信号，不触发真训练）。"""
        fb = LearningEffectFeedback(decay_threshold=0.2)
        pred, actual = _paired(ic=0.5)
        sig = fb.feedback("m1", predictions=pred, actuals=actual, baseline_ic=0.9)
        assert sig["retrain_recommended"] is True
        assert sig["triggered_training"] is False  # 红线：回喂不直接触发训练

    def test_feedback_healthy_when_no_decay(self):
        fb = LearningEffectFeedback(decay_threshold=0.2)
        pred, actual = _paired(ic=0.95)
        sig = fb.feedback("m1", predictions=pred, actuals=actual, baseline_ic=0.9)
        assert sig["retrain_recommended"] is False

    def test_feedback_history_accumulates(self):
        fb = LearningEffectFeedback()
        pred, actual = _paired()
        fb.feedback("m1", predictions=pred, actuals=actual, baseline_ic=0.8)
        fb.feedback("m1", predictions=pred, actuals=actual, baseline_ic=0.8)
        assert len(fb.history("m1")) == 2
        assert fb.history("ghost") == []
