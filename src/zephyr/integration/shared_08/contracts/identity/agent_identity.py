# [BLUEPRINT] SRC-181 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.identity.agent_identity
# [DOMAIN] D-INTEGRATION
# [DEPENDENCIES] zephyr.integration.shared_08.agent_identity_impl
# [CONSUMERS] zephyr.security.access_control.identity;zephyr.infrastructure.escalation;zephyr.governance;zephyr.integration.mcp
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] contract_purity: re-export only; impl in zephyr.integration.shared_08.agent_identity_impl
# [MODIFY-GUARD] zephyr.integration.shared_08.agent_identity_impl
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError if source module missing
# [TESTS] python -c "from zephyr.integration.shared_08.contracts.identity.agent_identity import AgentIdentity, MaturityLevel, AgentRole, IDESource"
# [A_module] module_id=MOD-INT_agent_identity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

from zephyr.integration.shared_08.agent_identity_impl import (
    MATURITY_AUTO_GUARD_TIMEOUT,
    MATURITY_TLB_LIMITS,
    ROLE_DEFAULT_PERMISSIONS,
    AgentIdentity,
    AgentMaturity,
    AgentRole,
    IDESource,
    MaturityLevel,
)

__all__ = [
    "MATURITY_AUTO_GUARD_TIMEOUT",
    "MATURITY_TLB_LIMITS",
    "ROLE_DEFAULT_PERMISSIONS",
    "AgentIdentity",
    "AgentMaturity",
    "AgentRole",
    "IDESource",
    "MaturityLevel",
]
