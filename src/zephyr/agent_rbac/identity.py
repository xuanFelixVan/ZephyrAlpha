# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.identity

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""
Agent 身份模型 — re-exported from shared.contracts.identity.

Canonical definition: zephyr.shared.contracts.identity.agent_identity
"""

from zephyr.shared.contracts.identity.agent_identity import (
    AgentIdentity,
    AgentMaturity,
    AgentRole,
    IDESource,
    MATURITY_AUTO_GUARD_TIMEOUT,
    MATURITY_TLB_LIMITS,
    MaturityLevel,
    ROLE_DEFAULT_PERMISSIONS,
)

__all__ = [
    "AgentIdentity",
    "AgentMaturity",
    "AgentRole",
    "IDESource",
    "MATURITY_AUTO_GUARD_TIMEOUT",
    "MATURITY_TLB_LIMITS",
    "MaturityLevel",
    "ROLE_DEFAULT_PERMISSIONS",
]
