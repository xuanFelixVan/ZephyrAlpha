# [BLUEPRINT] SRC-188 | docs/03_modules/_domain_governance/blueprint.md
# [MODULE] zephyr.shared.evaluation.evals
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] tests
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_evals.py
# [A_module] module_id=MOD-INT_evals | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class EvalDimension(Enum):
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    SAFETY = "safety"


@dataclass
class DimensionScore:
    dimension: EvalDimension
    score: float


@dataclass
class EvalCase:
    case_id: str
    input: str
    expected_output: str
    tags: list[str] = field(default_factory=list)
    threshold: float = 0.7
    metadata: dict = field(default_factory=dict)


@dataclass
class EvalRubric:
    dimensions: list[EvalDimension] = field(
        default_factory=lambda: [EvalDimension.RELEVANCE, EvalDimension.ACCURACY, EvalDimension.SAFETY]
    )
    weights: dict[str, float] = field(default_factory=dict)
    pass_threshold: float = 0.7

    def __post_init__(self) -> None:
        if not self.weights:
            n = len(self.dimensions)
            w = 1.0 / n if n > 0 else 0.0
            self.weights = {d.value: w for d in self.dimensions}


@dataclass
class EvalResult:
    case_id: str
    passed: bool
    overall_score: float
    dimension_scores: list[DimensionScore] = field(default_factory=list)
    actual_output: str = ""
    error: str | None = None

    @property
    def summary(self) -> str:
        tag = "[PASS]" if self.passed else "[FAIL]"
        return f"{tag} case={self.case_id} score={self.overall_score:.2f}"


@dataclass
class EvalSuiteResult:
    results: list[EvalResult] = field(default_factory=list)
    suite_name: str = ""

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
        return self.pass_count / self.total if self.total > 0 else 0.0

    @property
    def mean_score(self) -> float:
        return sum(r.overall_score for r in self.results) / self.total if self.total > 0 else 0.0


class EvalRunner:
    def __init__(self, rubric: EvalRubric | None = None) -> None:
        self._rubric = rubric or EvalRubric()
        self._cases: list[EvalCase] = []
        self._baselines: dict[str, float] = {}

    def add_case(self, case: EvalCase) -> None:
        self._cases.append(case)

    def add_cases(self, cases: list[EvalCase]) -> None:
        self._cases.extend(cases)

    def run_all(
        self, eval_fn: Callable[[str, str], tuple[float, list[DimensionScore]]], suite_name: str = ""
    ) -> EvalSuiteResult:
        results: list[EvalResult] = []
        for case in self._cases:
            result = self.run_single(case, eval_fn)
            results.append(result)
        return EvalSuiteResult(results=results, suite_name=suite_name)

    def run_single(
        self, case: EvalCase, eval_fn: Callable[[str, str], tuple[float, list[DimensionScore]]]
    ) -> EvalResult:
        try:
            score, dims = eval_fn(case.input, case.expected_output)
            return EvalResult(
                case_id=case.case_id,
                passed=score >= case.threshold,
                overall_score=score,
                dimension_scores=dims,
            )
        except Exception as exc:
            return EvalResult(
                case_id=case.case_id,
                passed=False,
                overall_score=0.0,
                error=str(exc),
            )

    def set_baseline(self, case_id: str, score: float) -> None:
        self._baselines[case_id] = score

    def check_regression(self, case_id: str, current_score: float) -> dict[str, object]:
        baseline = self._baselines.get(case_id)
        if baseline is None:
            return {"regression": False, "reason": "no_baseline"}
        delta = current_score - baseline
        return {"regression": delta < 0, "delta": delta}

    @staticmethod
    def simple_evaluate(actual: str, expected: str) -> tuple[float, list[DimensionScore]]:
        if not expected:
            return 0.0, []
        actual_words = set(actual.lower().split())
        expected_words = set(expected.lower().split())
        if not expected_words:
            return 0.0, []
        intersection = actual_words & expected_words
        union = actual_words | expected_words
        jaccard = len(intersection) / len(union) if union else 0.0
        containment = len(intersection) / len(expected_words) if expected_words else 0.0
        relevance = containment
        accuracy = jaccard
        safety = 1.0 if any(w in actual.lower() for w in expected.lower().split()) else 0.5
        score = (relevance + accuracy + safety) / 3.0
        dims = [
            DimensionScore(EvalDimension.RELEVANCE, relevance),
            DimensionScore(EvalDimension.ACCURACY, accuracy),
            DimensionScore(EvalDimension.SAFETY, safety),
        ]
        return score, dims


__all__ = [
    "DimensionScore",
    "EvalCase",
    "EvalDimension",
    "EvalResult",
    "EvalRubric",
    "EvalRunner",
    "EvalSuiteResult",
]
