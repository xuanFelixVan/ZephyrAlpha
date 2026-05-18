# [BLUEPRINT] MOD-INF-016 | 03_modules/_cross_layer/shared-core/blueprint.md | §
# [MODULE] zephyr.shared.contracts.identity
# [INVARIANTS] Agent身份模型不可被篡改;权限判定枚举不可扩展
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.agent_rbac;zephyr.escalation_engine;zephyr.governance;zephyr.mcp
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_agent_rbac.py

from zephyr.shared.contracts.identity.agent_identity import (
    AgentIdentity,
    AgentRole,
    AgentMaturity,
    IDESource,
    MaturityLevel,
    MATURITY_AUTO_GUARD_TIMEOUT,
    MATURITY_TLB_LIMITS,
    ROLE_DEFAULT_PERMISSIONS,
)
from zephyr.shared.contracts.identity.permission import GuardDecision, GuardResult

__all__ = [
    "AgentIdentity",
    "AgentMaturity",
    "AgentRole",
    "GuardDecision",
    "GuardResult",
    "IDESource",
    "MATURITY_AUTO_GUARD_TIMEOUT",
    "MATURITY_TLB_LIMITS",
    "MaturityLevel",
    "ROLE_DEFAULT_PERMISSIONS",
]
