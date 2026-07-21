# [A_test] module_id: MOD-GOV_evals_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-635 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_evals
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for evals.py
"""

import pytest

from zephyr.shared.evaluation.evals import (
    DimensionScore,
    EvalCase,
    EvalDimension,
    EvalResult,
    EvalRubric,
    EvalRunner,
    EvalSuiteResult,
)


class TestEvalCase:
    def test_create_basic(self):
        case = EvalCase(case_id="c1", input="hello", expected_output="hello world")
        assert case.case_id == "c1"
        assert case.threshold == 0.7
        assert case.tags == []

    def test_create_with_tags(self):
        case = EvalCase(case_id="c2", input="test", expected_output="test", tags=["unit", "smoke"], threshold=0.8)
        assert case.tags == ["unit", "smoke"]
        assert case.threshold == 0.8


class TestEvalRubric:
    def test_default_rubric(self):
        rubric = EvalRubric()
        assert len(rubric.dimensions) == 3
        assert EvalDimension.RELEVANCE in rubric.dimensions

    def test_custom_weights(self):
        rubric = EvalRubric(weights={"relevance": 0.5, "accuracy": 0.3, "completeness": 0.2})
        assert rubric.weights["relevance"] == 0.5

    def test_auto_weights_equal(self):
        rubric = EvalRubric()
        for w in rubric.weights.values():
            assert w == pytest.approx(1.0 / 3)

    def test_pass_threshold(self):
        rubric = EvalRubric(pass_threshold=0.8)
        assert rubric.pass_threshold == 0.8


class TestEvalResult:
    def test_summary_pass(self):
        result = EvalResult(
            case_id="c1",
            passed=True,
            overall_score=0.85,
            dimension_scores=[
                DimensionScore(EvalDimension.RELEVANCE, 0.9),
                DimensionScore(EvalDimension.ACCURACY, 0.8),
            ],
        )
        assert "[PASS]" in result.summary
        assert "c1" in result.summary

    def test_summary_fail(self):
        result = EvalResult(
            case_id="c2",
            passed=False,
            overall_score=0.45,
            dimension_scores=[
                DimensionScore(EvalDimension.RELEVANCE, 0.3),
            ],
        )
        assert "[FAIL]" in result.summary

    def test_with_error(self):
        result = EvalResult(case_id="c3", passed=False, overall_score=0.0, error="evaluation failed")
        assert result.error == "evaluation failed"
        assert not result.passed


class TestEvalSuiteResult:
    def test_empty_suite(self):
        suite = EvalSuiteResult(results=[])
        assert suite.total == 0
        assert suite.pass_rate == 0.0
        assert suite.mean_score == 0.0

    def test_all_pass(self):
        suite = EvalSuiteResult(
            results=[
                EvalResult("c1", True, 0.9),
                EvalResult("c2", True, 0.85),
            ]
        )
        assert suite.pass_count == 2
        assert suite.fail_count == 0
        assert suite.pass_rate == 1.0
        assert suite.mean_score == 0.875

    def test_mixed(self):
        suite = EvalSuiteResult(
            results=[
                EvalResult("c1", True, 0.9),
                EvalResult("c2", False, 0.5),
            ]
        )
        assert suite.pass_count == 1
        assert suite.fail_count == 1
        assert suite.pass_rate == 0.5


class TestEvalRunner:
    def test_add_and_run(self):
        runner = EvalRunner()

        def mock_eval(_input, _expected):
            return (0.85, [DimensionScore(EvalDimension.RELEVANCE, 0.85)])

        runner.add_case(EvalCase("c1", "in", "out"))
        suite = runner.run_all(mock_eval)

        assert suite.total == 1
        assert suite.pass_count == 1

    def test_run_all_with_error(self):
        runner = EvalRunner()

        def failing_eval(_input, _expected):
            raise RuntimeError("eval failed")

        runner.add_case(EvalCase("c1", "in", "out"))
        suite = runner.run_all(failing_eval)

        assert suite.total == 1
        assert suite.fail_count == 1
        assert suite.results[0].error is not None

    def test_regression_detected(self):
        runner = EvalRunner()
        runner.set_baseline("c1", 0.90)
        result = runner.check_regression("c1", 0.80)
        assert result["regression"] is True
        assert result["delta"] == -0.1

    def test_regression_not_detected(self):
        runner = EvalRunner()
        runner.set_baseline("c1", 0.90)
        result = runner.check_regression("c1", 0.92)
        assert result["regression"] is False

    def test_regression_no_baseline(self):
        runner = EvalRunner()
        result = runner.check_regression("c1", 0.90)
        assert result["regression"] is False
        assert result["reason"] == "no_baseline"

    def test_simple_evaluate_perfect_match(self):
        overall, dims = EvalRunner.simple_evaluate("hello world", "hello world")
        assert overall == pytest.approx(1.0)

    def test_simple_evaluate_partial_match(self):
        overall, dims = EvalRunner.simple_evaluate("hello", "hello world today")
        assert 0 < overall < 1.0

    def test_simple_evaluate_empty_expected(self):
        overall, dims = EvalRunner.simple_evaluate("test", "")
        assert overall == 0.0

    def test_run_single(self):
        runner = EvalRunner()

        def mock_eval(_input, _expected):
            return (0.92, [DimensionScore(EvalDimension.ACCURACY, 0.92)])

        result = runner.run_single(EvalCase("c1", "in", "out"), mock_eval)
        assert result.passed
        assert result.overall_score == 0.92
