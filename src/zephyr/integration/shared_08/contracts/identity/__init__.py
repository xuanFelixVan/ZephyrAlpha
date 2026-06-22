# [A_module] module_id=MOD-INT_identity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-180 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.identity
# [INVARIANTS] Agent身份模型不可被篡改;权限判定枚举不可扩展
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.access_control;zephyr.security.escalation;zephyr.governance;zephyr.integration.mcp
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_agent_rbac.py

from zephyr.integration.shared_08.contracts.identity.agent_identity import (
    MATURITY_AUTO_GUARD_TIMEOUT,
    MATURITY_TLB_LIMITS,
    ROLE_DEFAULT_PERMISSIONS,
    AgentIdentity,
    AgentMaturity,
    AgentRole,
    IDESource,
    MaturityLevel,
)
from zephyr.integration.shared_08.contracts.identity.permission import GuardDecision, GuardResult

__all__ = [
    "MATURITY_AUTO_GUARD_TIMEOUT",
    "MATURITY_TLB_LIMITS",
    "ROLE_DEFAULT_PERMISSIONS",
    "AgentIdentity",
    "AgentMaturity",
    "AgentRole",
    "GuardDecision",
    "GuardResult",
    "IDESource",
    "MaturityLevel",
    "agent_identity",
    "permission",
]
