# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.confidence_estimator
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 置信度评估必须基于历史数据;校准不可跳过
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_confidence_estimator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Confidence Estimator — D-022-05 置信度评估器: certainty×evidence×risk三维评估。
"""

from __future__ import annotations


class ConfidenceLevel:
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ConfidenceEstimator:
    def evaluate(self, certainty: float, evidence: float, risk: float) -> str:
        score = certainty * 0.4 + evidence * 0.35 + (1.0 - risk) * 0.25
        if score >= 0.7:
            return ConfidenceLevel.HIGH
        if score >= 0.4:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    def should_auto_execute(self, certainty: float, evidence: float, risk: float) -> bool:
        return self.evaluate(certainty, evidence, risk) == ConfidenceLevel.HIGH and risk < 0.3
