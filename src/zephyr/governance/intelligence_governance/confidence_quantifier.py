# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.confidence_quantifier
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF_confidence_quantifier | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ConfidenceQuantifier — AI 置信度量化。

依据: 蓝图 MOD-INF-021 §7 Phase 9 + §6.16 B114 + exit code 37

对 AI agent 每次操作输出量化置信度 (0.0 ~ 1.0):
    连续 5 次低置信 (< 0.3) -> exit 37 (LOW_CONFIDENCE_CONSEC) -> tier 降低
    连续 10 次低置信 -> 暂停该 agent session
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ConfidenceRecord:
    operation_id: str
    confidence: float
    tier: str
    timestamp: str


@dataclass
class ConfidenceResult:
    average_confidence: float
    consecutive_low: int
    tier: str
    action: str
    exit_code: int


class ConfidenceQuantifier:
    EXIT_CODE_LOW_CONFIDENCE: int = 37
    LOW_THRESHOLD: float = 0.30
    MAX_CONSECUTIVE_LOW: int = 5
    MAX_TOTAL_LOW: int = 10

    def __init__(self) -> None:
        self._history: list[ConfidenceRecord] = []
        self._consecutive_low = 0

    def record(self, operation_id: str, confidence: float) -> ConfidenceResult:
        tier = self._determine_tier(confidence)

        self._history.append(
            ConfidenceRecord(
                operation_id=operation_id,
                confidence=confidence,
                tier=tier,
                timestamp="",
            )
        )

        if confidence < self.LOW_THRESHOLD:
            self._consecutive_low += 1
        else:
            self._consecutive_low = 0

        avg = self.average_confidence
        action = "normal"
        exit_code = 0

        if self._consecutive_low >= self.MAX_CONSECUTIVE_LOW:
            action = "REDUCE_TIER"
            exit_code = self.EXIT_CODE_LOW_CONFIDENCE

        total_low = sum(1 for r in self._history if r.confidence < self.LOW_THRESHOLD)
        if total_low >= self.MAX_TOTAL_LOW:
            action = "SUSPEND_AGENT"
            exit_code = self.EXIT_CODE_LOW_CONFIDENCE

        return ConfidenceResult(
            average_confidence=avg,
            consecutive_low=self._consecutive_low,
            tier=tier,
            action=action,
            exit_code=exit_code,
        )

    @property
    def average_confidence(self) -> float:
        if not self._history:
            return 1.0
        return sum(r.confidence for r in self._history) / len(self._history)

    @property
    def current_tier(self) -> str:
        return self._determine_tier(self.average_confidence)

    @staticmethod
    def _determine_tier(confidence: float) -> str:
        if confidence >= 0.80:
            return "TIER_1_FULL_AUTO"
        elif confidence >= 0.50:
            return "TIER_2_AUTO_WITH_AUDIT"
        elif confidence >= 0.30:
            return "TIER_3_HUMAN_REVIEW"
        else:
            return "TIER_4_HUMAN_ONLY"

    @property
    def history(self) -> list[ConfidenceRecord]:
        return self._history
