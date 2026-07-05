# [BLUEPRINT] SRC-073 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.offline_resilience
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.resilience_governance.__init__
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
# [A_module] module_id=MOD-GOV_offline_resilience | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

from __future__ import annotations

from enum import Enum


class TIFLevel(str, Enum):
    L1 = "L1_<5m"
    L2 = "L2_5-30m"
    L3 = "L3_30m-4h"
    L4 = "L4_4-24h"
    L5 = "L5_24h+"


DECAY_START_HOURS: int = 8
DECAY_RATE_PER_24H: float = 0.25
MAX_DECAY_HOURS: int = 72

E2E_TARGET_MS: int = 460
E2E_BUDGET_BREAKDOWN_MS: dict[str, int] = {
    "MARKETDATA": 405,
    "SIGNAL": 1000,
    "RISK": 50,
}
