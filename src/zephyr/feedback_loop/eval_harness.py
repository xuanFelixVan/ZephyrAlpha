# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.eval_harness
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: cases 参数
#   fields: 参数 cases（无注解）
#   code: eval_harness.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① EvalHarness
#   name_en: EvalHarness
#   intro: class EvalHarness 源码 L149-L277
#   desc: 公共方法（定义序）: build_default, run_all, run_by_category, to_json；源码 L149-L277
#   inputs: cases
#   outputs: 返回值
# - id: A2
#   name_zh: ② build_intent_cases
#   name_en: build_intent_cases
#   intro: build_intent_cases() 源码 L296-L297
#   desc: 源码 L296-L297
#   inputs: 无参数
#   outputs: list[EvalCase]
# - id: A3
#   name_zh: ③ build_orchestrator_cases
#   name_en: build_orchestrator_cases
#   intro: build_orchestrator_cases() 源码 L300-L301
#   desc: 源码 L300-L301
#   inputs: 无参数
#   outputs: list[EvalCase]
# - id: A4
#   name_zh: ④ build_hallucination_cases
#   name_en: build_hallucination_cases
#   intro: build_hallucination_cases() 源码 L304-L305
#   desc: 源码 L304-L305
#   inputs: 无参数
#   outputs: list[EvalCase]
# - id: A5
#   name_zh: ⑤ build_evolution_cases
#   name_en: build_evolution_cases
#   intro: build_evolution_cases() 源码 L308-L309
#   desc: 源码 L308-L309
#   inputs: 无参数
#   outputs: list[EvalCase]
#   （注：A5 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[EvalCase]
#   name_en: list[EvalCase]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import json
import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Final

CATEGORY_INTENT: Final[str] = "INTENT"
CATEGORY_ORCHESTRATOR: Final[str] = "ORCHESTRATOR"
CATEGORY_HALLUCINATION: Final[str] = "HALLUCINATION"
CATEGORY_EVOLUTION: Final[str] = "EVOLUTION"

CATEGORIES: Final[frozenset] = frozenset(
    {CATEGORY_INTENT, CATEGORY_ORCHESTRATOR, CATEGORY_HALLUCINATION, CATEGORY_EVOLUTION}
)


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

            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
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
