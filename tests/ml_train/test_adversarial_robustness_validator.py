# [BLUEPRINT] MOD-ML-005 | docs/03_modules/_domain_machine_learning_train/blueprint.md
# [MODULE] tests.ml_train.test_adversarial_robustness_validator
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [TESTS] pytest tests/ml_train/test_adversarial_robustness_validator.py -q
# [TTL] permanent

"""对抗鲁棒性验证器（MOD-ML-005）单元测试——噪声扰动下预测漂移/准确率降级报告。"""

from __future__ import annotations

import numpy as np
import pytest

from zephyr.ml_train.adversarial_robustness_validator import (
    AdversarialValidationError,
    RobustnessReport,
    validate_robustness,
)


def _identity_predict(x: np.ndarray) -> np.ndarray:
    return x[:, 0]


class TestInputValidation:
    def test_empty_samples_rejected(self):
        with pytest.raises(AdversarialValidationError):
            validate_robustness(_identity_predict, np.array([]))

    def test_non_finite_samples_rejected(self):
        with pytest.raises(AdversarialValidationError):
            validate_robustness(_identity_predict, np.array([[np.nan, 1.0]]))

    def test_bad_epsilon_rejected(self):
        with pytest.raises(AdversarialValidationError):
            validate_robustness(_identity_predict, np.ones((5, 2)), epsilons=(-0.1,))
        with pytest.raises(AdversarialValidationError):
            validate_robustness(_identity_predict, np.ones((5, 2)), epsilons=())

    def test_bad_trials_rejected(self):
        with pytest.raises(AdversarialValidationError):
            validate_robustness(_identity_predict, np.ones((5, 2)), n_trials=0)

    def test_label_length_mismatch_rejected(self):
        with pytest.raises(AdversarialValidationError):
            validate_robustness(_identity_predict, np.ones((5, 2)), labels=np.ones(3))


class TestRobustnessReport:
    def test_report_shape_and_determinism(self):
        x = np.random.default_rng(0).normal(size=(30, 4))
        r1 = validate_robustness(_identity_predict, x, epsilons=(0.01, 0.1), n_trials=4, seed=7)
        r2 = validate_robustness(_identity_predict, x, epsilons=(0.01, 0.1), n_trials=4, seed=7)
        assert isinstance(r1, RobustnessReport)
        assert [p.epsilon for p in r1.points] == [0.01, 0.1]
        assert r1.points[0].mean_shift == pytest.approx(r2.points[0].mean_shift)

    def test_stronger_model_shifts_less(self):
        x = np.random.default_rng(1).normal(size=(40, 3))
        fragile = validate_robustness(lambda v: v.sum(axis=1) * 100, x, epsilons=(0.5,), n_trials=4, seed=3)
        robust = validate_robustness(lambda v: np.zeros(len(v)), x, epsilons=(0.5,), n_trials=4, seed=3)
        assert robust.points[0].mean_shift < fragile.points[0].mean_shift

    def test_accuracy_drop_with_labels(self):
        x = np.tile(np.array([[1.0, 0.0], [-1.0, 0.0]]), (20, 1))
        y = np.tile(np.array([1.0, -1.0]), 20)
        report = validate_robustness(
            _identity_predict, x, labels=y, epsilons=(0.0, 2.0), n_trials=4, seed=5, decision_threshold=0.0
        )
        assert report.baseline_accuracy == pytest.approx(1.0)
        assert report.points[1].accuracy <= report.points[0].accuracy

    def test_zero_epsilon_zero_shift(self):
        x = np.random.default_rng(2).normal(size=(10, 3))
        report = validate_robustness(_identity_predict, x, epsilons=(0.0,), n_trials=2, seed=1)
        assert report.points[0].mean_shift == pytest.approx(0.0)

    def test_error_code(self):
        assert AdversarialValidationError.error_code == "ZA-MLT-0009"
