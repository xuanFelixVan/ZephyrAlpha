# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md
# [MODULE] zephyr.governance.context_governance.context_manager
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] MOD-INF-020;MOD-INF-018;MOD-INF-027
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Token/Cost/Time三维预算;超预算拒绝
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/budget-enforcer/blueprint.md;src/zephyr/budget-enforcer/__init__.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] BudgetExceededError;CostLimitError
# [TESTS] tests/test_budget_enforcer/
# [A_module] module_id=MOD-RES_context_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum


class TokenTier(str, Enum):
    T0 = "T0_500"
    T1 = "T1_2K"
    T2 = "T2_5K"
    T3 = "T3_18K"
    T4 = "T4_40K"


TIER_TOKENS: dict[TokenTier, int] = {
    TokenTier.T0: 500,
    TokenTier.T1: 2000,
    TokenTier.T2: 5000,
    TokenTier.T3: 18000,
    TokenTier.T4: 40000,
}


class HallucinationLevel(str, Enum):
    L1_FACT = "L1_fact_inconsistency"
    L2_BLUEPRINT = "L2_blueprint_conflict"
    L3_SELF_REF = "L3_self_refuting"


TRIM_DUPLICATE_THRESHOLD: float = 0.30
MAX_HISTORY_DAYS: int = 30
