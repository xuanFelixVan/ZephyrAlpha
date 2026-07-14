# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.offline_resilience
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.offline_resilience
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_offline_resilience | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export shim: canonical source = zephyr.infrastructure.a2a_protocol.offline_resilience (SSoT 收敛，消除多真源)

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.offline_resilience import (
    DECAY_RATE_PER_24H,
    DECAY_START_HOURS,
    E2E_BUDGET_BREAKDOWN_MS,
    E2E_TARGET_MS,
    MAX_DECAY_HOURS,
    TIFLevel,
)

__all__ = [
    "DECAY_RATE_PER_24H",
    "DECAY_START_HOURS",
    "E2E_BUDGET_BREAKDOWN_MS",
    "E2E_TARGET_MS",
    "MAX_DECAY_HOURS",
    "TIFLevel",
]
