# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_debt_score
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_context_debt_score | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""context_debt_score.py — 上下文债务评分 (B19, DD93, TASK-017)"""

from dataclasses import dataclass


@dataclass
class DebtScore:
    ke_id: str
    age_days: float
    conflict_count: int
    ref_staleness: float
    deprecation_risk: float
    deprecated: bool


class ContextDebtScorer:
    """per-KE deprecation_risk = age * conflict * ref_staleness; >0.7 → [DEPRECATED] (DD93)."""

    def score(self, ke_id: str, age_days: float, conflict_count: int, ref_staleness: float) -> DebtScore:
        risk = (age_days / 365) * max(1, conflict_count) * max(0.1, ref_staleness)
        risk_clamped = min(1.0, risk)
        return DebtScore(
            ke_id=ke_id,
            age_days=age_days,
            conflict_count=conflict_count,
            ref_staleness=ref_staleness,
            deprecation_risk=round(risk_clamped, 3),
            deprecated=risk_clamped > 0.7,
        )
