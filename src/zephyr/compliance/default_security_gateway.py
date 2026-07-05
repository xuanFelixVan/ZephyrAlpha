# [BLUEPRINT] MOD-L10-001
# [MODULE] zephyr.compliance.default_security_gateway
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.governance.security_governance.default_security_gateway
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
# Re-export shim: canonical source = zephyr.governance.security_governance.default_security_gateway (SSoT 收敛，消除多真源)

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
