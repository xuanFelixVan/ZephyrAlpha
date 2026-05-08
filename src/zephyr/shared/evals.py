"""
evals.py —— AI 输出质量评估框架（Phase 12 | 盲点 B29）

痛点修复：有 contract tests（代码正确性），缺 Agent 输出质量系统评估。

设计对标：
  - PydanticAI Evals: 结构化 eval 用例 + 评分 rubrics
  - LangChain eval harness: 批量 eval runner
  - OpenAI evals: 回归检测 + 评分一致性

AI 施工约定：
  - 每次 Agent 输出 SHOULD 通过 EvalRunner 评估
  - EvalResult 中的 score < 0.6 MUST 触发人工审查
  - 回归检测发现退化 MUST 阻断 pipeline

SSoT: MOD-INF-016 §12 盲点 B29
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum, unique
from typing import Any, Callable


@unique
class EvalDimension(str, Enum):
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    SAFETY = "safety"
    EFFICIENCY = "efficiency"


@dataclass
class EvalCase:
    """单个评估用例——输入 + 期望输出 + 元数据。"""

    case_id: str
    input: str
    expected_output: str
    tags: list[str] = field(default_factory=list)
    threshold: float = 0.7
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass
class EvalRubric:
    """评分标准——多维度评分权重与阈值定义。"""

    dimensions: list[EvalDimension] = field(default_factory=lambda: [
        EvalDimension.RELEVANCE,
        EvalDimension.ACCURACY,
        EvalDimension.COMPLETENESS,
    ])
    weights: dict[str, float] = field(default_factory=dict)
    pass_threshold: float = 0.7

    def __post_init__(self) -> None:
        if not self.weights:
            n = len(self.dimensions)
            self.weights = {d.value: 1.0 / n for d in self.dimensions}


@dataclass
class DimensionScore:
    """单维度评分结果。"""

    dimension: EvalDimension
    score: float
    explanation: str = ""


@dataclass
class EvalResult:
    """单个 eval case 的评估结果。"""

    case_id: str
    passed: bool
    overall_score: float
    dimension_scores: list[DimensionScore] = field(default_factory=list)
    actual_output: str = ""
    error: str | None = None
    evaluated_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        dims = ", ".join(f"{ds.dimension.value}={ds.score:.2f}" for ds in self.dimension_scores)
        return f"[{status}] {self.case_id}: {self.overall_score:.2f} ({dims})"


@dataclass
class EvalSuiteResult:
    """批量评估结果。"""

    results: list[EvalResult] = field(default_factory=list)
    suite_name: str = ""
    executed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    @property
    def pass_count(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def fail_count(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def pass_rate(self) -> float:
        if not self.results:
            return 0.0
        return self.pass_count / self.total

    @property
    def mean_score(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.overall_score for r in self.results) / self.total


class EvalRunner:
    """批量评估执行器。

    Usage::

        runner = EvalRunner(rubric=EvalRubric())
        runner.add_case(EvalCase("c1", "input", "expected"))
        suite = runner.run_all(evaluate_fn=my_eval_fn)
        print(f"Pass rate: {suite.pass_rate:.1%}")
    """

    def __init__(self, rubric: EvalRubric | None = None):
        self.rubric = rubric or EvalRubric()
        self.cases: list[EvalCase] = []
        self._baseline: dict[str, float] = {}

    def add_case(self, case: EvalCase) -> None:
        self.cases.append(case)

    def add_cases(self, cases: list[EvalCase]) -> None:
        self.cases.extend(cases)

    def run_all(
        self,
        evaluate_fn: Callable[[str, str], tuple[float, list[DimensionScore]]],
        suite_name: str = "",
    ) -> EvalSuiteResult:
        results: list[EvalResult] = []
        for case in self.cases:
            try:
                overall, dims = evaluate_fn(case.input, case.expected_output)
                passed = overall >= case.threshold
                results.append(EvalResult(
                    case_id=case.case_id,
                    passed=passed,
                    overall_score=overall,
                    dimension_scores=dims,
                ))
            except Exception as e:
                results.append(EvalResult(
                    case_id=case.case_id,
                    passed=False,
                    overall_score=0.0,
                    error=str(e),
                ))
        return EvalSuiteResult(results=results, suite_name=suite_name)

    def run_single(
        self,
        case: EvalCase,
        evaluate_fn: Callable[[str, str], tuple[float, list[DimensionScore]]],
    ) -> EvalResult:
        try:
            overall, dims = evaluate_fn(case.input, case.expected_output)
            return EvalResult(
                case_id=case.case_id,
                passed=overall >= case.threshold,
                overall_score=overall,
                dimension_scores=dims,
            )
        except Exception as e:
            return EvalResult(
                case_id=case.case_id,
                passed=False,
                overall_score=0.0,
                error=str(e),
            )

    def set_baseline(self, case_id: str, score: float) -> None:
        self._baseline[case_id] = score

    def check_regression(self, case_id: str, current_score: float) -> dict[str, Any]:
        """回归检测——当前分数是否低于基线。"""
        baseline = self._baseline.get(case_id)
        if baseline is None:
            return {"regression": False, "reason": "no_baseline", "delta": 0.0}
        delta = current_score - baseline
        return {
            "regression": delta < -0.05,
            "reason": "regression_detected" if delta < -0.05 else "ok",
            "delta": round(delta, 4),
            "baseline": baseline,
            "current": current_score,
        }

    @staticmethod
    def simple_evaluate(
        actual: str,
        expected: str,
    ) -> tuple[float, list[DimensionScore]]:
        """简单评估——基于字符串相似度的启发式评分。"""
        if not expected:
            return (0.0, [])

        actual_lower = actual.lower()
        expected_lower = expected.lower()

        words_actual = set(actual_lower.split())
        words_expected = set(expected_lower.split())
        relevance = len(words_actual & words_expected) / max(len(words_expected), 1)

        if expected_lower == actual_lower:
            accuracy = 1.0
        elif expected_lower in actual_lower or actual_lower in expected_lower:
            accuracy = 0.7
        else:
            accuracy = 0.3

        completeness = min(1.0, len(actual) / max(len(expected), 1))

        overall = relevance * 0.4 + accuracy * 0.35 + completeness * 0.25
        overall = min(1.0, max(0.0, overall))

        return (
            overall,
            [
                DimensionScore(EvalDimension.RELEVANCE, relevance, f"word overlap: {relevance:.2f}"),
                DimensionScore(EvalDimension.ACCURACY, accuracy, f"string match: {accuracy:.2f}"),
                DimensionScore(EvalDimension.COMPLETENESS, completeness, f"length ratio: {completeness:.2f}"),
            ],
        )


__all__ = [
    "EvalDimension",
    "EvalCase",
    "EvalRubric",
    "DimensionScore",
    "EvalResult",
    "EvalSuiteResult",
    "EvalRunner",
]
