# [A_test] module_id: MOD-GOV_evals_shared | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-566 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.shared.test_evals
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
单元测试：src/zephyr/shared/evals.py
=====================================
覆盖矩阵：
  EvalCase：
    - 构造 × 1
    - 默认值 × 1
  EvalRubric：
    - 默认权重分配 × 1
    - 自定义权重 × 1
  EvalResult：
    - passed / failed 判断 × 2
    - summary 格式化 × 2
  EvalSuiteResult：
    - pass_count / fail_count / total × 1
    - pass_rate × 2（含空集）
    - mean_score × 2（含空集）
   EvalRunner：
    - 空 runner 返回 EvalSuiteResult × 1
    - run_all 标准流程 × 1
    - run_all 异常 case 不阻断 × 1
    - run_single × 1
    - set_baseline / check_regression × 3
  EvalRunner.simple_evaluate：
    - 完全匹配 × 1
    - 部分匹配 × 1
    - 不匹配 × 1
    - 空 expected × 1

Safety: MEDIUM（评估框架不影响代码执行安全）
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
    def test_construction(self):
        case = EvalCase(
            case_id="c1",
            input="What is 2+2?",
            expected_output="4",
            tags=["math", "basic"],
            threshold=0.8,
        )
        assert case.case_id == "c1"
        assert case.input == "What is 2+2?"
        assert case.expected_output == "4"
        assert case.tags == ["math", "basic"]
        assert case.threshold == 0.8

    def test_defaults(self):
        case = EvalCase(case_id="c2", input="x", expected_output="y")
        assert case.tags == []
        assert case.threshold == 0.7
        assert case.metadata == {}


class TestEvalRubric:
    def test_default_weights(self):
        rubric = EvalRubric()
        assert len(rubric.weights) == 3
        total = sum(rubric.weights.values())
        assert total == pytest.approx(1.0)
        assert rubric.pass_threshold == 0.7

    def test_custom_weights(self):
        rubric = EvalRubric(
            dimensions=[EvalDimension.RELEVANCE, EvalDimension.SAFETY],
            weights={"relevance": 0.6, "safety": 0.4},
        )
        assert rubric.weights["relevance"] == 0.6
        assert rubric.weights["safety"] == 0.4


class TestEvalResult:
    def test_passed_result(self):
        result = EvalResult(
            case_id="c1",
            passed=True,
            overall_score=0.85,
            dimension_scores=[
                DimensionScore(EvalDimension.RELEVANCE, 0.9),
                DimensionScore(EvalDimension.ACCURACY, 0.8),
            ],
        )
        assert result.passed is True
        assert result.summary.startswith("[PASS]")

    def test_failed_result(self):
        result = EvalResult(
            case_id="c2",
            passed=False,
            overall_score=0.45,
        )
        assert result.passed is False
        assert result.summary.startswith("[FAIL]")

    def test_default_actual_output(self):
        result = EvalResult(case_id="c3", passed=True, overall_score=1.0)
        assert result.actual_output == ""


class TestEvalSuiteResult:
    def test_aggregate_statistics(self):
        suite = EvalSuiteResult(
            results=[
                EvalResult(case_id="a", passed=True, overall_score=0.9),
                EvalResult(case_id="b", passed=True, overall_score=0.8),
                EvalResult(case_id="c", passed=False, overall_score=0.5),
            ],
            suite_name="regression-test",
        )
        assert suite.pass_count == 2
        assert suite.fail_count == 1
        assert suite.total == 3
        assert suite.pass_rate == pytest.approx(2 / 3)
        assert suite.mean_score == pytest.approx((0.9 + 0.8 + 0.5) / 3)

    def test_empty_suite(self):
        suite = EvalSuiteResult()
        assert suite.total == 0
        assert suite.pass_rate == 0.0
        assert suite.mean_score == 0.0


class TestEvalRunner:
    @staticmethod
    def _passing_eval_fn(inp: str, expected: str):
        return (0.95, [DimensionScore(EvalDimension.RELEVANCE, 0.95)])

    @staticmethod
    def _failing_eval_fn(inp: str, expected: str):
        return (0.4, [DimensionScore(EvalDimension.RELEVANCE, 0.4)])

    @staticmethod
    def _throwing_eval_fn(inp: str, expected: str):
        raise RuntimeError("eval error")

    def test_empty_runner(self):
        runner = EvalRunner()
        suite = runner.run_all(self._passing_eval_fn)
        assert isinstance(suite, EvalSuiteResult)
        assert suite.total == 0

    def test_run_all_standard(self):
        runner = EvalRunner(rubric=EvalRubric())
        runner.add_cases(
            [
                EvalCase(case_id="c1", input="?", expected_output="ans", threshold=0.7),
                EvalCase(case_id="c2", input="?", expected_output="ans", threshold=0.7),
            ]
        )
        suite = runner.run_all(self._passing_eval_fn, suite_name="test")
        assert suite.pass_count == 2
        assert suite.total == 2
        assert suite.suite_name == "test"

    def test_run_all_handles_exceptions(self):
        runner = EvalRunner()
        runner.add_case(EvalCase(case_id="err", input="x", expected_output="y"))
        suite = runner.run_all(self._throwing_eval_fn)
        assert suite.total == 1
        assert suite.fail_count == 1
        assert suite.results[0].error is not None

    def test_run_single(self):
        runner = EvalRunner()
        case = EvalCase(case_id="s1", input="q", expected_output="a")
        result = runner.run_single(case, self._passing_eval_fn)
        assert result.passed is True
        assert result.overall_score == 0.95

    def test_set_baseline_and_check_no_regression(self):
        runner = EvalRunner()
        runner.set_baseline("c1", 0.8)
        check = runner.check_regression("c1", 0.85)
        assert check["regression"] is False
        assert check["delta"] == pytest.approx(0.05)

    def test_check_regression_detected(self):
        runner = EvalRunner()
        runner.set_baseline("c1", 0.9)
        check = runner.check_regression("c1", 0.8)
        assert check["regression"] is True
        assert check["delta"] == pytest.approx(-0.1)

    def test_check_regression_no_baseline(self):
        runner = EvalRunner()
        check = runner.check_regression("c1", 0.9)
        assert check["regression"] is False
        assert check["reason"] == "no_baseline"


class TestSimpleEvaluate:
    def test_exact_match(self):
        score, dims = EvalRunner.simple_evaluate("hello world", "hello world")
        assert score == pytest.approx(1.0)
        assert len(dims) == 3

    def test_partial_match(self):
        score, dims = EvalRunner.simple_evaluate(
            "hello world foo bar",
            "hello world baz qux",
        )
        assert 0.0 < score < 1.0

    def test_no_match(self):
        score, dims = EvalRunner.simple_evaluate("aaaaa", "bbbbb")
        assert 0.0 <= score < 0.5

    def test_empty_expected(self):
        score, dims = EvalRunner.simple_evaluate("something", "")
        assert score == 0.0
        assert dims == []

    def test_substring_match(self):
        score, dims = EvalRunner.simple_evaluate("the answer is 42", "answer is")
        assert 0.5 < score < 1.0
