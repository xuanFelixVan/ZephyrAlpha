# [A_test] module_id: SRC-TST-1407 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_prompt_optimization_regression_detector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.evolution.prompt_optimization_regression_detector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_prompt_optimization_regression_detector.py
# [TTL] task_bound

import pytest

from zephyr.feedback_loop.evolution.prompt_optimization_regression_detector import (
    PromptOptimizationRegressionDetector,
)


class TestPromptOptimizationRegressionDetectorInstantiation:
    def test_default_instantiation(self):
        obj = PromptOptimizationRegressionDetector()
        assert obj is not None
        assert obj.min_test_samples == 10
        assert obj.significance_level == pytest.approx(0.05)

    def test_custom_params(self):
        obj = PromptOptimizationRegressionDetector(min_test_samples=20, significance_level=0.01)
        assert obj.min_test_samples == 20
        assert obj.significance_level == pytest.approx(0.01)

    def test_is_dataclass(self):
        obj = PromptOptimizationRegressionDetector()
        assert hasattr(obj, "__dataclass_fields__")


class TestPromptOptimizationRegressionDetectorRunABTest:
    def test_insufficient_samples_reject(self):
        pord = PromptOptimizationRegressionDetector()
        old = [0.8] * 5
        new = [0.9] * 5
        result = pord.run_ab_test(old_results=old, new_results=new)
        assert result["status"] == "insufficient_samples"
        assert result["decision"] == "REJECT"

    def test_sufficient_samples_returns_metrics(self):
        pord = PromptOptimizationRegressionDetector(min_test_samples=5)
        old = [0.7, 0.75, 0.72, 0.73, 0.71, 0.74, 0.70, 0.76, 0.72, 0.73]
        new = [0.85, 0.87, 0.86, 0.84, 0.88, 0.86, 0.87, 0.85, 0.86, 0.84]
        result = pord.run_ab_test(old_results=old, new_results=new)
        assert "old_mean" in result
        assert "new_mean" in result
        assert "improvement" in result
        assert "p_value" in result
        assert "t_statistic" in result

    def test_improvement_positive(self):
        pord = PromptOptimizationRegressionDetector(min_test_samples=5)
        old = [0.5] * 15
        new = [0.9] * 15
        result = pord.run_ab_test(old_results=old, new_results=new)
        assert result["improvement"] > 0

    def test_regression_negative_improvement(self):
        pord = PromptOptimizationRegressionDetector(min_test_samples=5)
        old = [0.9] * 15
        new = [0.5] * 15
        result = pord.run_ab_test(old_results=old, new_results=new)
        assert result["improvement"] < 0
        assert result["status"] == "REJECT"


class TestPromptOptimizationRegressionDetectorBoundaries:
    def test_identical_results(self):
        pord = PromptOptimizationRegressionDetector(min_test_samples=5)
        vals = [0.75] * 15
        result = pord.run_ab_test(old_results=vals, new_results=vals)
        assert result["improvement"] == pytest.approx(0.0)

    def test_empty_old_results(self):
        pord = PromptOptimizationRegressionDetector()
        result = pord.run_ab_test(old_results=[], new_results=[0.9] * 15)
        assert result["status"] == "insufficient_samples"

    def test_empty_new_results(self):
        pord = PromptOptimizationRegressionDetector()
        result = pord.run_ab_test(old_results=[0.9] * 15, new_results=[])
        assert result["status"] == "insufficient_samples"

    def test_exactly_min_samples(self):
        pord = PromptOptimizationRegressionDetector(min_test_samples=10)
        old = [0.7 + 0.01 * i for i in range(10)]
        new = [0.8 + 0.01 * i for i in range(10)]
        result = pord.run_ab_test(old_results=old, new_results=new)
        assert result["status"] in ("ALLOW", "REJECT")
