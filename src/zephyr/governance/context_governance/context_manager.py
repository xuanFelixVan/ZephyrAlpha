# [A_module] module_id=MOD-GOV_context_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-027 | docs/03_modules/_domain-governance/blueprint.md | §

# [MODULE] zephyr.governance.context_manager

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

from __future__ import annotations
from enum import Enum

class TokenTier(str, Enum):
    T0 = "T0_500"
    T1 = "T1_2K"
    T2 = "T2_5K"
    T3 = "T3_18K"
    T4 = "T4_40K"

TIER_TOKENS: dict[TokenTier, int] = {
    TokenTier.T0: 500, TokenTier.T1: 2000, TokenTier.T2: 5000,
    TokenTier.T3: 18000, TokenTier.T4: 40000,
}

class HallucinationLevel(str, Enum):
    L1_FACT = "L1_fact_inconsistency"
    L2_BLUEPRINT = "L2_blueprint_conflict"
    L3_SELF_REF = "L3_self_refuting"

TRIM_DUPLICATE_THRESHOLD: float = 0.30
MAX_HISTORY_DAYS: int = 30
