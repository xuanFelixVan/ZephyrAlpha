# [BLUEPRINT] SRC-068 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] zephyr.governance.resilience_governance.bus_factor_defense
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.factor.bus_factor_defense
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
# [A_module] module_id=MOD-GOV_bus_factor_defense | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export shim: canonical source = zephyr.factor.bus_factor_defense (SSoT 收敛，消除多真源)

from __future__ import annotations

from zephyr.factor.bus_factor_defense import (
    BusFactorRisk,
    DecisionLog,
    ModuleOwnership,
    OpsRunbook,
    check_bus_factor,
    create_decision_log,
    generate_runbook,
)

__all__ = [
    "BusFactorRisk",
    "DecisionLog",
    "ModuleOwnership",
    "OpsRunbook",
    "check_bus_factor",
    "create_decision_log",
    "generate_runbook",
]
