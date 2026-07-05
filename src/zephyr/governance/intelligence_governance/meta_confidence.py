# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.meta_confidence
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 元置信度评估不可跳过;自评偏差必须校准
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_meta_confidence | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Meta-Confidence — D-022-10 Agent对自身判定置信度的自评+历史校准。
"""

from __future__ import annotations


class MetaConfidence:
    def __init__(self):
        self._history: list[tuple[float, float, bool]] = []

    def self_assess(self, confidence: float, evidence_count: int, domain_familiarity: float) -> float:
        ev_score = min(1.0, evidence_count / 5.0)
        return confidence * 0.5 + ev_score * 0.3 + domain_familiarity * 0.2

    def calibrate(self, predicted: float, actual_correct: bool):
        self._history.append((predicted, 0.0, actual_correct))

    def calibration_error(self) -> float:
        if not self._history:
            return 0.0
        return sum(abs(p - (1.0 if c else 0.0)) for p, _, c in self._history) / len(self._history)
