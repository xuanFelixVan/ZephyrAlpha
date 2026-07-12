# [A_test] module_id: SRC-TST-0561 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_confidence_decomposer
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.confidence_decomposer
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_confidence_decomposer.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.diagnosers.confidence_decomposer import ConfidenceDecomposer


class TestConfidenceDecomposerInstantiation:
    def test_default_instantiation(self):
        cd = ConfidenceDecomposer()
        assert cd is not None


class TestConfidenceDecomposerDecompose:
    def test_decompose_even_split(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(0.9, {"data_quality": 1.0, "model_certainty": 1.0})
        assert "data_quality" in result
        assert "model_certainty" in result
        assert abs(result["data_quality"] - 0.45) < 1e-9
        assert abs(result["model_certainty"] - 0.45) < 1e-9

    def test_decompose_three_factors(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(0.6, {"a": 1, "b": 2, "c": 3})
        assert len(result) == 3
        expected = 0.6 / 3
        for v in result.values():
            assert abs(v - expected) < 1e-9

    def test_decompose_single_factor(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(0.8, {"only_one": 1.0})
        assert abs(result["only_one"] - 0.8) < 1e-9

    def test_decompose_zero_confidence(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(0.0, {"a": 1, "b": 2})
        for v in result.values():
            assert v == 0.0

    def test_decompose_empty_factors(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(0.9, {})
        assert result == {}

    def test_decompose_preserves_keys(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(1.0, {"x": 0, "y": 0, "z": 0})
        assert set(result.keys()) == {"x", "y", "z"}

    def test_decompose_sum_approximates_confidence(self):
        cd = ConfidenceDecomposer()
        confidence = 0.75
        factors = {"f1": 1, "f2": 1, "f3": 1}
        result = cd.decompose(confidence, factors)
        total = sum(result.values())
        assert abs(total - confidence) < 1e-9


class TestConfidenceDecomposerBoundary:
    def test_decompose_negative_confidence(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(-0.5, {"a": 1})
        assert result["a"] < 0

    def test_decompose_confidence_above_one(self):
        cd = ConfidenceDecomposer()
        result = cd.decompose(2.0, {"a": 1, "b": 1})
        assert result["a"] >= 1.0

    def test_decompose_none_factors_raises(self):
        cd = ConfidenceDecomposer()
        with pytest.raises((TypeError, AttributeError)):
            cd.decompose(0.5, None)

    def test_decompose_none_confidence_raises(self):
        cd = ConfidenceDecomposer()
        with pytest.raises((TypeError, AttributeError)):
            cd.decompose(None, {"a": 1})
