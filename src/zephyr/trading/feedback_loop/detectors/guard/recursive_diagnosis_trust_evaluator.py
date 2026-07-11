# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.detectors.guard.recursive_diagnosis_trust_evaluator
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.trading.feedback_loop.detectors.__init__
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
# [A_module] module_id=MOD-UNK_recursive_diagnosis_trust_evaluator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
R517: RecursiveDiagnosisTrustEvaluator
自诊断vs外部信号交叉验证 — 信外部不信自诊
"""

from dataclasses import dataclass, field


@dataclass
class ExternalSignal:
    source: str
    value: float
    threshold: float
    direction: str


@dataclass
class RecursiveDiagnosisTrustEvaluator:
    external_signals: dict[str, ExternalSignal] = field(default_factory=dict)
    self_diagnosis_history: list[dict] = field(default_factory=list)
    max_history: int = 50

    def register_external_signal(self, name: str, value: float, threshold: float, direction: str = "above") -> None:
        self.external_signals[name] = ExternalSignal(
            source=name,
            value=value,
            threshold=threshold,
            direction=direction,
        )

    def update_external_signal(self, name: str, value: float) -> None:
        if name in self.external_signals:
            self.external_signals[name].value = value

    def evaluate_trust(self, self_diagnosis: dict) -> dict:
        self.self_diagnosis_history.append(self_diagnosis)
        if len(self.self_diagnosis_history) > self.max_history:
            self.self_diagnosis_history = self.self_diagnosis_history[-self.max_history :]

        external_verdict = self._aggregate_external_signals()
        self_verdict = self_diagnosis.get("status", "unknown")

        trust_score = self._compute_trust_score(self_verdict, external_verdict)

        return {
            "self_diagnosis_status": self_verdict,
            "external_verdict": external_verdict,
            "trust-score": round(trust - score, 3),
            "trustworthy": trust - score >= 0.5,
            "recommendation": "trust_self"
            if trust - score >= 0.7
            else ("trust_external" if trust - score < 0.5 else "inconclusive"),
        }

    def _aggregate_external_signals(self) -> str:
        if not self.external_signals:
            return "unknown"

        unhealthy_count = 0
        for signal in self.external_signals.values():
            if signal.direction == "above":
                if signal.value > signal.threshold:
                    unhealthy_count += 1
            elif signal.direction == "below":
                if signal.value < signal.threshold:
                    unhealthy_count += 1

        ratio = unhealthy_count / len(self.external_signals)
        if ratio >= 0.5:
            return "unhealthy"
        elif ratio >= 0.25:
            return "degraded"
        return "healthy"

    def _compute_trust_score(self, self_verdict: str, external_verdict: str) -> float:
        if self_verdict == external_verdict:
            return 0.9
        if self_verdict == "unknown" or external_verdict == "unknown":
            return 0.4
        healthy_pairs = [
            ("healthy", "degraded"),
            ("degraded", "unhealthy"),
        ]
        for h, d in healthy_pairs:
            if (self_verdict == h and external_verdict == d) or (self_verdict == d and external_verdict == h):
                return 0.3
        return 0.1
