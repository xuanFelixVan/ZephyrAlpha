# [A_test] module_id: SRC-TST-0958 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_eval_harness
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.eval_harness
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_eval_harness.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.eval_harness import (
    CATEGORY_INTENT,
    EvalCase,
    EvalHarness,
    EvalOutcome,
)


class TestEvalHarnessInstantiation:
    def test_creates_with_defaults(self):
        harness = EvalHarness()
        assert harness.cases == []

    def test_creates_with_cases(self):
        cases = [EvalCase(case_id="t1", category=CATEGORY_INTENT, runner=lambda: EvalOutcome(passed=True))]
        harness = EvalHarness(cases=cases)
        assert len(harness.cases) == 1


class TestRunAll:
    def test_empty_harness(self):
        harness = EvalHarness()
        report = harness.run_all()
        assert report.total == 0
        assert report.pass_rate == 0.0

    def test_passing_case(self):
        case = EvalCase(case_id="t1", category=CATEGORY_INTENT, runner=lambda: EvalOutcome(passed=True))
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        assert report.passed == 1
        assert report.pass_rate == 1.0

    def test_failing_case(self):
        case = EvalCase(case_id="t1", category=CATEGORY_INTENT, runner=lambda: EvalOutcome(passed=False))
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        assert report.failed == 1

    def test_no_runner_marks_error(self):
        case = EvalCase(case_id="t1", category=CATEGORY_INTENT)
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        assert report.passed == 0
        assert "no_runner" in report.error_breakdown

    def test_exception_in_runner(self):
        def bad_runner():
            raise RuntimeError("boom")

        case = EvalCase(case_id="t1", category=CATEGORY_INTENT, runner=bad_runner)
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        assert report.failed == 1
        assert "RuntimeError" in report.error_breakdown


class TestRunByCategory:
    def test_valid_category(self):
        case = EvalCase(case_id="t1", category=CATEGORY_INTENT, runner=lambda: EvalOutcome(passed=True))
        harness = EvalHarness(cases=[case])
        report = harness.run_by_category(CATEGORY_INTENT)
        assert report.total == 1

    def test_invalid_category_raises(self):
        harness = EvalHarness()
        with pytest.raises(ValueError, match="Unknown category"):
            harness.run_by_category("INVALID")


class TestToJson:
    def test_serializes_report(self):
        case = EvalCase(case_id="t1", category=CATEGORY_INTENT, runner=lambda: EvalOutcome(passed=True))
        harness = EvalHarness(cases=[case])
        report = harness.run_all()
        json_str = EvalHarness.to_json(report)
        assert "total" in json_str
        assert "passed" in json_str
