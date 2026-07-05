# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.rule_enforcement.output_quality_gate
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-RES_output_quality_gate | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
from dataclasses import dataclass


@dataclass
class QualityRule:
    name: str
    check_fn: str
    threshold: float
    severity: str


@dataclass
class QualityVerdict:
    passed: bool
    score: float
    violations: list[str]
    should_block: bool


DEFAULT_RULES: list[QualityRule] = [
    QualityRule("min_length", "len>20", 0.5, "soft"),
    QualityRule("no_repetition", "unique_ratio>0.3", 0.5, "soft"),
    QualityRule("no_placeholder", "placeholder_count==0", 1.0, "hard"),
    QualityRule("cost_per_char", "cost/len<0.01", 0.7, "soft"),
    QualityRule("format_valid", "has_delimiters", 0.8, "soft"),
]


class OutputQualityGate:
    def __init__(self, rules: list[QualityRule] | None = None):
        self._rules = rules or DEFAULT_RULES

    def evaluate(self, output: str, cost: float) -> QualityVerdict:
        violations: list[str] = []
        scores: list[float] = []

        token_estimate = len(output) // 4

        scores.append(self._check_min_length(output))
        if scores[-1] < self._rule_threshold("min_length"):
            violations.append(f"输出过短: {len(output)} chars")

        scores.append(self._check_repetition(output))
        if scores[-1] < self._rule_threshold("no_repetition"):
            violations.append("输出重复度过高")

        scores.append(self._check_placeholder(output))
        if scores[-1] == 0.0:
            violations.append("包含占位符文本")

        scores.append(self._check_cost_efficiency(output, cost))
        if scores[-1] < self._rule_threshold("cost_per_char"):
            violations.append(f"成本效率低: cost={cost:.4f} len={len(output)}")

        scores.append(self._check_format(output))
        if scores[-1] < self._rule_threshold("format_valid"):
            violations.append("输出格式异常")

        avg_score = sum(scores) / len(scores) if scores else 1.0
        hard_violations = [v for v in violations if self._severity_for(v) == "hard"]
        should_block = len(hard_violations) > 0

        return QualityVerdict(
            passed=not should_block and avg_score >= 0.6,
            score=avg_score,
            violations=violations,
            should_block=should_block,
        )

    def _check_min_length(self, text: str) -> float:
        if len(text) < 10:
            return 0.0
        if len(text) < 30:
            return 0.5
        return 1.0

    def _check_repetition(self, text: str) -> float:
        if len(text) < 20:
            return 1.0
        words = text.split()
        if not words:
            return 1.0
        unique_ratio = len(set(words)) / len(words)
        return unique_ratio

    def _check_placeholder(self, text: str) -> float:
        placeholders = ["TODO", "FIXME", "[placeholder]", "Lorem ipsum", "..."]
        for p in placeholders:
            if p.lower() in text.lower():
                return 0.0
        return 1.0

    def _check_cost_efficiency(self, text: str, cost: float) -> float:
        if len(text) == 0:
            return 0.0
        ratio = cost / len(text)
        if ratio < 0.0001:
            return 1.0
        if ratio < 0.001:
            return 0.8
        if ratio < 0.01:
            return 0.5
        return 0.2

    def _check_format(self, text: str) -> float:
        score = 1.0
        if text.count("{") != text.count("}"):
            score -= 0.3
        if text.count("(") != text.count(")"):
            score -= 0.3
        if text.count("[") != text.count("]"):
            score -= 0.3
        return max(score, 0.0)

    def _rule_threshold(self, name: str) -> float:
        for r in self._rules:
            if r.name == name:
                return r.threshold
        return 0.5

    def _severity_for(self, violation: str) -> str:
        if "占位符" in violation:
            return "hard"
        return "soft"

    def add_rule(self, rule: QualityRule) -> None:
        self._rules.append(rule)
