# [A_test] module_id: SRC-TST-2017 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-634 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_eval_harness
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
# AI-generated: T-3-22 (A27) · EvalHarness 单元测试
"""
test_eval_harness · EvalHarness 单元测试
==========================================

Task ID     : T-3-22 (A27)
safety_level: H

覆盖要求（来自 -cards.md T-3-22）
---------------------------------------

- 类别配比：10 intent + 10 orchestrator + 5 hallucination + 5 evolution
- 每个用例具备 input → expected → actual → pass/fail 契约
- 汇总报告：pass_rate / avg_latency / error_breakdown
- 单元测试 ≥ 20 条

本测试文件总计 ≥ 25 条 test，分 6 个测试类：

1. TestEvalHarnessCaseCount        — 用例数量/分布/唯一 case_id
2. TestEvalHarnessExecution        — run_all / run_by_category / outcome
3. TestEvalHarnessReport           — pass_rate / avg_latency / error_breakdown
4. TestEvalHarnessJSON             — to_json 的序列化契约
5. TestEvalHarnessBuilders         — 每个 build_*_cases 的独立契约
6. TestEvalHarnessDefaultCases     — 默认 30 用例集成 PASS
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from zephyr.feedback_loop.eval_harness import (
    CATEGORIES,
    CATEGORY_EVOLUTION,
    CATEGORY_HALLUCINATION,
    CATEGORY_INTENT,
    CATEGORY_ORCHESTRATOR,
    EvalCase,
    EvalHarness,
    EvalOutcome,
    build_evolution_cases,
    build_hallucination_cases,
    build_intent_cases,
    build_orchestrator_cases,
)

# ---------------------------------------------------------------------------
# 1. Case count / distribution
# ---------------------------------------------------------------------------


class TestEvalHarnessCaseCount:
    def test_default_harness_has_thirty_cases(self) -> None:
        h = EvalHarness.build_default()
        assert len(h.cases) == 30

    def test_intent_has_ten_cases(self) -> None:
        assert len(build_intent_cases()) == 10

    def test_orchestrator_has_ten_cases(self) -> None:
        assert len(build_orchestrator_cases()) == 10

    def test_hallucination_has_five_cases(self) -> None:
        assert len(build_hallucination_cases()) == 5

    def test_evolution_has_five_cases(self) -> None:
        assert len(build_evolution_cases()) == 5

    def test_case_ids_unique(self) -> None:
        cases = EvalHarness.build_default().cases
        ids = [c.case_id for c in cases]
        assert len(set(ids)) == len(ids)

    def test_case_category_membership_valid(self) -> None:
        for c in EvalHarness.build_default().cases:
            assert c.category in CATEGORIES


# ---------------------------------------------------------------------------
# 2. Execution behaviour
# ---------------------------------------------------------------------------


class TestEvalHarnessExecution:
    def test_run_all_returns_30_results(self) -> None:
        report = EvalHarness.build_default().run_all()
        assert report.total == 30
        assert len(report.cases) == 30

    def test_run_by_category_intent_only(self) -> None:
        report = EvalHarness.build_default().run_by_category(CATEGORY_INTENT)
        assert report.total == 10
        assert all(r.category == CATEGORY_INTENT for r in report.cases)

    def test_run_by_category_unknown_raises(self) -> None:
        with pytest.raises(ValueError):
            EvalHarness.build_default().run_by_category("does-not-exist")

    def test_runner_exception_counts_as_failure_without_crash(self) -> None:
        def bad() -> EvalOutcome:
            raise RuntimeError("boom")

        h = EvalHarness([EvalCase("BAD-01", CATEGORY_INTENT, "intentional crash", bad)])
        report = h.run_all()
        assert report.failed == 1
        assert report.cases[0].error is not None
        assert "RuntimeError" in report.cases[0].error

    def test_outcome_pass_and_fail_branches(self) -> None:
        cases = [
            EvalCase(
                "OK-01",
                CATEGORY_INTENT,
                "pass",
                lambda: EvalOutcome(passed=True, expected=1, actual=1),
            ),
            EvalCase(
                "NG-01",
                CATEGORY_INTENT,
                "fail",
                lambda: EvalOutcome(passed=False, expected=1, actual=2),
            ),
        ]
        report = EvalHarness(cases).run_all()
        assert report.passed == 1
        assert report.failed == 1


# ---------------------------------------------------------------------------
# 3. Report fields
# ---------------------------------------------------------------------------


class TestEvalHarnessReport:
    def test_pass_rate_is_fraction(self) -> None:
        cases = [
            EvalCase(
                f"R-{i}",
                CATEGORY_INTENT,
                "x",
                lambda i=i: EvalOutcome(passed=bool(i % 2), expected=0, actual=0),
            )
            for i in range(4)
        ]
        report = EvalHarness(cases).run_all()
        assert 0.0 <= report.pass_rate <= 1.0
        assert report.pass_rate == pytest.approx(report.passed / report.total)

    def test_avg_latency_non_negative(self) -> None:
        report = EvalHarness.build_default().run_all()
        assert report.avg_latency_ms >= 0.0

    def test_error_breakdown_counts_exceptions(self) -> None:
        cases = [
            EvalCase(
                "E-1",
                CATEGORY_INTENT,
                "err1",
                lambda: (_ for _ in ()).throw(RuntimeError("x")),
            ),
            EvalCase(
                "E-2",
                CATEGORY_INTENT,
                "err2",
                lambda: (_ for _ in ()).throw(ValueError("y")),
            ),
        ]
        report = EvalHarness(cases).run_all()
        assert report.error_breakdown.get("RuntimeError") == 1
        assert report.error_breakdown.get("ValueError") == 1

    def test_error_breakdown_tracks_assertion_failures(self) -> None:
        case = EvalCase(
            "A-1",
            CATEGORY_INTENT,
            "assert fail",
            lambda: EvalOutcome(passed=False, expected=1, actual=2),
        )
        report = EvalHarness([case]).run_all()
        assert report.error_breakdown.get("assertion") == 1

    def test_by_category_present_only_for_present_categories(self) -> None:
        cases = [
            EvalCase(
                "I-1",
                CATEGORY_INTENT,
                "x",
                lambda: EvalOutcome(passed=True, expected=1, actual=1),
            )
        ]
        report = EvalHarness(cases).run_all()
        assert CATEGORY_INTENT in report.by_category
        assert CATEGORY_EVOLUTION not in report.by_category

    def test_by_category_counts_match_total(self) -> None:
        report = EvalHarness.build_default().run_all()
        assert sum(s.total for s in report.by_category.values()) == report.total


# ---------------------------------------------------------------------------
# 4. JSON serialization
# ---------------------------------------------------------------------------


class TestEvalHarnessJSON:
    def test_to_json_roundtrip(self) -> None:
        report = EvalHarness.build_default().run_all()
        blob = EvalHarness.to_json(report)
        data: dict[str, Any] = json.loads(blob)
        assert data["total"] == 30
        assert 0.0 <= data["pass_rate"] <= 1.0

    def test_to_json_includes_cases(self) -> None:
        report = EvalHarness.build_default().run_all()
        data: dict[str, Any] = json.loads(EvalHarness.to_json(report))
        assert len(data["cases"]) == 30
        assert {"case_id", "category", "passed", "expected", "actual", "latency_ms"}.issubset(data["cases"][0].keys())

    def test_to_json_by_category_shape(self) -> None:
        report = EvalHarness.build_default().run_all()
        data: dict[str, Any] = json.loads(EvalHarness.to_json(report))
        for key in (
            CATEGORY_INTENT,
            CATEGORY_ORCHESTRATOR,
            CATEGORY_HALLUCINATION,
            CATEGORY_EVOLUTION,
        ):
            assert key in data["by_category"]
            entry = data["by_category"][key]
            assert entry["total"] >= 1
            assert 0.0 <= entry["pass_rate"] <= 1.0


# ---------------------------------------------------------------------------
# 5. Builders
# ---------------------------------------------------------------------------


class TestEvalHarnessBuilders:
    def test_intent_cases_all_pass_smoke(self) -> None:
        report = EvalHarness(build_intent_cases()).run_all()
        assert report.passed == report.total
        assert report.total == 10

    def test_orchestrator_cases_all_pass_smoke(self) -> None:
        report = EvalHarness(build_orchestrator_cases()).run_all()
        assert report.passed == report.total
        assert report.total == 10

    def test_hallucination_cases_all_pass_smoke(self) -> None:
        report = EvalHarness(build_hallucination_cases()).run_all()
        assert report.passed == report.total
        assert report.total == 5

    def test_evolution_cases_all_pass_smoke(self) -> None:
        report = EvalHarness(build_evolution_cases()).run_all()
        assert report.passed == report.total
        assert report.total == 5

    def test_each_case_has_callable_runner(self) -> None:
        for c in EvalHarness.build_default().cases:
            assert callable(c.runner)
            assert c.description
            assert c.case_id.startswith("IE-")


# ---------------------------------------------------------------------------
# 6. Default integration
# ---------------------------------------------------------------------------


class TestEvalHarnessDefaultCases:
    def test_default_all_pass(self) -> None:
        report = EvalHarness.build_default().run_all()
        assert report.passed == 30
        assert report.pass_rate == pytest.approx(1.0)

    def test_custom_cases_replace_defaults(self) -> None:
        case = EvalCase(
            "CUSTOM-01",
            CATEGORY_INTENT,
            "custom",
            lambda: EvalOutcome(passed=True, expected=1, actual=1),
        )
        h = EvalHarness([case])
        assert len(h.cases) == 1
        assert h.cases[0].case_id == "CUSTOM-01"
