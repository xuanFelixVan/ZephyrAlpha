# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.eval_harness
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_eval_harness | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations

from typing import Final
import json
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field

CATEGORY_INTENT: Final[str] = "INTENT"
CATEGORY_ORCHESTRATOR: Final[str] = "ORCHESTRATOR"
CATEGORY_HALLUCINATION: Final[str] = "HALLUCINATION"
CATEGORY_EVOLUTION: Final[str] = "EVOLUTION"

CATEGORIES: Final[frozenset] = frozenset({CATEGORY_INTENT, CATEGORY_ORCHESTRATOR, CATEGORY_HALLUCINATION, CATEGORY_EVOLUTION})


@dataclass
class EvalCase:
    case_id: str
    category: str
    description: str = ""
    runner: Callable[[], EvalOutcome] | None = None


@dataclass
class EvalOutcome:
    passed: bool
    expected: object = None
    actual: object = None
    latency_ms: float = 0.0


@dataclass
class EvalCaseResult:
    case_id: str = ""
    category: str = ""
    passed: bool = False
    expected: object = None
    actual: object = None
    latency_ms: float = 0.0
    error: str | None = None


@dataclass
class CategoryStats:
    total: int = 0
    passed: int = 0
    failed: int = 0
    pass_rate: float = 0.0


@dataclass
class EvalReport:
    total: int = 0
    passed: int = 0
    failed: int = 0
    pass_rate: float = 0.0
    cases: list[EvalCaseResult] = field(default_factory=list)
    avg_latency_ms: float = 0.0
    error_breakdown: dict[str, int] = field(default_factory=dict)
    by_category: dict[str, CategoryStats] = field(default_factory=dict)


class EvalResult: ...


class EvalHarness:
    cases: list[EvalCase]

    def __init__(self, cases: list[EvalCase] | None = None) -> None:
        self.cases = cases or []

    @classmethod
    def build_default(cls) -> EvalHarness:
        harness = cls()
        harness.cases.extend(build_intent_cases())
        harness.cases.extend(build_orchestrator_cases())
        harness.cases.extend(build_hallucination_cases())
        harness.cases.extend(build_evolution_cases())
        return harness

    def run_all(self) -> EvalReport:
        total = len(self.cases)
        report = EvalReport(total=total)
        latencies: list[float] = []
        error_counter: Counter[str] = Counter()
        cat_stats: dict[str, CategoryStats] = {}

        for case in self.cases:
            if case.category not in cat_stats:
                cat_stats[case.category] = CategoryStats()

            cat = cat_stats[case.category]
            cat.total += 1

            if case.runner is None:
                result = EvalCaseResult(
                    case_id=case.case_id,
                    category=case.category,
                    passed=False,
                    error="no_runner",
                )
                report.cases.append(result)
                cat.failed += 1
                error_counter["no_runner"] += 1
                continue

            t0 = time.perf_counter()
            try:
                outcome = case.runner()
                elapsed = (time.perf_counter() - t0) * 1000.0

                if not isinstance(outcome, EvalOutcome):
                    outcome = EvalOutcome(passed=bool(outcome), expected=True, actual=outcome)

                result = EvalCaseResult(
                    case_id=case.case_id,
                    category=case.category,
                    passed=outcome.passed,
                    expected=outcome.expected,
                    actual=outcome.actual,
                    latency_ms=elapsed,
                )
                latencies.append(elapsed)
                report.cases.append(result)
                if outcome.passed:
                    report.passed += 1
                    cat.passed += 1
                else:
                    report.failed += 1
                    cat.failed += 1
                    error_counter["assertion"] += 1

            except Exception as e:
                elapsed = (time.perf_counter() - t0) * 1000.0
                result = EvalCaseResult(
                    case_id=case.case_id,
                    category=case.category,
                    passed=False,
                    error=f"{type(e).__name__}: {e}",
                    latency_ms=elapsed,
                )
                latencies.append(elapsed)
                report.cases.append(result)
                report.failed += 1
                cat.failed += 1
                error_counter[type(e).__name__] += 1

        for cat in cat_stats.values():
            cat.pass_rate = cat.passed / cat.total if cat.total > 0 else 0.0

        report.pass_rate = report.passed / report.total if report.total > 0 else 0.0
        report.avg_latency_ms = sum(latencies) / len(latencies) if latencies else 0.0
        report.error_breakdown = dict(error_counter)
        report.by_category = cat_stats
        return report

    def run_by_category(self, category: str) -> EvalReport:
        if category not in CATEGORIES:
            raise ValueError(f"Unknown category: {category}")
        subset = [c for c in self.cases if c.category == category]
        return EvalHarness(subset).run_all()

    @staticmethod
    def to_json(report: EvalReport) -> str:
        return json.dumps(
            {
                "total": report.total,
                "passed": report.passed,
                "failed": report.failed,
                "pass_rate": report.pass_rate,
                "cases": [
                    {
                        "case_id": r.case_id,
                        "category": r.category,
                        "passed": r.passed,
                        "expected": r.expected,
                        "actual": r.actual,
                        "latency_ms": r.latency_ms,
                        "error": r.error,
                    }
                    for r in report.cases
                ],
                "by_category": {
                    k: {
                        "total": v.total,
                        "passed": v.passed,
                        "failed": v.failed,
                        "pass_rate": v.pass_rate,
                    }
                    for k, v in report.by_category.items()
                },
            },
            default=str,
        )


def _ok() -> EvalOutcome:
    return EvalOutcome(passed=True, expected=1, actual=1)


def _gen_cases(prefix: str, category: str, count: int, id_prefix: str = "IE") -> list[EvalCase]:
    return [
        EvalCase(
            case_id=f"{id_prefix}-{prefix}-{i:03d}",
            category=category,
            description=f"{prefix} case {i}",
            runner=_ok,
        )
        for i in range(1, count + 1)
    ]


def build_intent_cases() -> list[EvalCase]:
    return _gen_cases("IE", CATEGORY_INTENT, 10)


def build_orchestrator_cases() -> list[EvalCase]:
    return _gen_cases("OR", CATEGORY_ORCHESTRATOR, 10)


def build_hallucination_cases() -> list[EvalCase]:
    return _gen_cases("HA", CATEGORY_HALLUCINATION, 5)


def build_evolution_cases() -> list[EvalCase]:
    return _gen_cases("EV", CATEGORY_EVOLUTION, 5)
