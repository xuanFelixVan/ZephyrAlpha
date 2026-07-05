# [BLUEPRINT] MOD-L10-001 | docs/03_modules/_domain_compliance/blueprint.md
# [MODULE] zephyr.governance.implementations.default_security_gateway
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.security_governance.default_security_gateway
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
# [A_module] module_id=MOD-GOV_default_security_gateway | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Re-export shim: canonical source = zephyr.governance.security_governance.default_security_gateway (SSoT 收敛，消除多真源)

from __future__ import annotations

from zephyr.governance.security_governance.default_security_gateway import (
    DefaultSecurityGateway,
    ScanFinding,
    SecurityContext,
)

__all__ = [
    "DefaultSecurityGateway",
    "ScanFinding",
    "SecurityContext",
]
