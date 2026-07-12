# [A_test] module_id: SRC-TST-0578 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_conformal_prediction
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.conformal_prediction
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_conformal_prediction.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.conformal_prediction import ConformalPrediction


class TestConformalPredictionInstantiation:
    def test_default_instantiation(self):
        obj = ConformalPrediction()
        assert obj is not None

    def test_is_dataclass(self):
        obj = ConformalPrediction()
        assert hasattr(obj, "__dataclass_fields__")


class TestConformalPredictionPredictInterval:
    def test_positive_score(self):
        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=10.0)
        assert low == pytest.approx(8.0)
        assert high == pytest.approx(12.0)

    def test_zero_score(self):
        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=0.0)
        assert low == pytest.approx(0.0)
        assert high == pytest.approx(0.0)

    def test_negative_score(self):
        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=-5.0)
        assert low == pytest.approx(-4.0)
        assert high == pytest.approx(-6.0)

    def test_custom_alpha(self):
        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=10.0, alpha=0.1)
        assert isinstance(low, float)
        assert isinstance(high, float)

    def test_interval_contains_score(self):
        cp = ConformalPrediction()
        score = 7.5
        low, high = cp.predict_interval(score=score)
        assert low <= score <= high or high <= score <= low

    def test_returns_tuple(self):
        cp = ConformalPrediction()
        result = cp.predict_interval(score=5.0)
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestConformalPredictionBoundaries:
    def test_very_large_score(self):
        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=1e9)
        assert low == pytest.approx(8e8)
        assert high == pytest.approx(1.2e9)

    def test_very_small_score(self):
        cp = ConformalPrediction()
        low, high = cp.predict_interval(score=1e-9)
        assert isinstance(low, float)
        assert isinstance(high, float)
