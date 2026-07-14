# [BLUEPRINT] MOD-GOVERNANCE | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.offline_autonomy
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [DEPENDENCIES] zephyr.infrastructure.a2a_protocol.offline_autonomy
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
# [A_module] module_id=MOD-GOV_offline_autonomy | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export shim: canonical source = zephyr.infrastructure.a2a_protocol.offline_autonomy (SSoT 收敛，消除多真源)

from __future__ import annotations

from zephyr.infrastructure.a2a_protocol.offline_autonomy import (
    AutonomyState,
    OfflineMode,
)

__all__ = [
    "AutonomyState",
    "OfflineMode",
]
