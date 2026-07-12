# [A_test] module_id: SRC-TST-0861 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_eval_harness
# [INVARIANTS] EvalHarness.run_all returns EvalReport; pass_rate = passed/total when total>0
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import json

import pytest

from zephyr.feedback_loop.eval_harness import (
    CATEGORY_EVOLUTION,
    CATEGORY_HALLUCINATION,
    CATEGORY_INTENT,
    CATEGORY_ORCHESTRATOR,
    EvalCase,
    EvalHarness,
    EvalOutcome,
    EvalReport,
    build_evolution_cases,
    build_hallucination_cases,
    build_intent_cases,
    build_orchestrator_cases,
)


class TestEvalHarnessInstantiation:
    def test_default_init(self):
        harness = EvalHarness()
        assert harness.cases == []

    def test_init_with_cases(self):
        cases = [EvalCase(case_id="T-001", category=CATEGORY_INTENT)]
        harness = EvalHarness(cases=cases)
        assert len(harness.cases) == 1


class TestEvalHarnessBuildDefault:
    def test_build_default_contains_all_categories(self):
        harness = EvalHarness.build_default()
        categories = {c.category for c in harness.cases}
        assert CATEGORY_INTENT in categories
        assert CATEGORY_ORCHESTRATOR in categories
        assert CATEGORY_HALLUCINATION in categories
        assert CATEGORY_EVOLUTION in categories

    def test_build_default_has_30_cases(self):
        harness = EvalHarness.build_default()
        assert len(harness.cases) == 30


class TestEvalHarnessRunAll:
    def test_run_all_empty(self):
        harness = EvalHarness()
        report = harness.run_all()
        assert report.total == 0
        assert report.pass_rate == 0.0

    def test_run_all_passing_case(self):
        case = EvalCase(
            case_id="T-001",
            category=CATEGORY_INTENT,
            runner=lambda: EvalOutcome(passed=True),
        )
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        assert report.passed == 1
        assert report.failed == 0
        assert report.pass_rate == 1.0

    def test_run_all_failing_case(self):
        case = EvalCase(
            case_id="T-002",
            category=CATEGORY_INTENT,
            runner=lambda: EvalOutcome(passed=False),
        )
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        assert report.passed == 0
        assert report.failed == 1

    def test_run_all_no_runner(self):
        case = EvalCase(case_id="T-003", category=CATEGORY_INTENT)
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        assert report.passed == 0
        assert "no_runner" in report.error_breakdown

    def test_run_all_exception_in_runner(self):
        def bad_runner():
            raise RuntimeError("boom")

        case = EvalCase(case_id="T-004", category=CATEGORY_INTENT, runner=bad_runner)
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        assert report.failed == 1
        assert "RuntimeError" in report.error_breakdown


class TestEvalHarnessRunByCategory:
    def test_run_by_category_valid(self):
        harness = EvalHarness.build_default()
        report = harness.run_by_category(CATEGORY_INTENT)
        assert report.total > 0

    def test_run_by_category_invalid(self):
        harness = EvalHarness()
        with pytest.raises(ValueError, match="Unknown category"):
            harness.run_by_category("INVALID")


class TestEvalHarnessToJson:
    def test_to_json_valid(self):
        case = EvalCase(
            case_id="T-005",
            category=CATEGORY_INTENT,
            runner=lambda: EvalOutcome(passed=True),
        )
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        json_str = EvalHarness.to_json(report)
        parsed = json.loads(json_str)
        assert parsed["total"] == 1
        assert parsed["passed"] == 1

    def test_to_json_empty_report(self):
        report = EvalReport()
        json_str = EvalHarness.to_json(report)
        parsed = json.loads(json_str)
        assert parsed["total"] == 0


class TestBuildCases:
    def test_build_intent_cases(self):
        cases = build_intent_cases()
        assert len(cases) == 10
        assert all(c.category == CATEGORY_INTENT for c in cases)

    def test_build_orchestrator_cases(self):
        cases = build_orchestrator_cases()
        assert len(cases) == 10

    def test_build_hallucination_cases(self):
        cases = build_hallucination_cases()
        assert len(cases) == 5

    def test_build_evolution_cases(self):
        cases = build_evolution_cases()
        assert len(cases) == 5
