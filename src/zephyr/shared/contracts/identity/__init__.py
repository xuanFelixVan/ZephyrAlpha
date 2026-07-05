# [A_module] module_id=MOD-SHR_identity | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/blueprint.md
# [MODULE] zephyr.shared.contracts.identity
# [INVARIANTS] Agent身份模型不可被篡改;权限判定枚举不可扩展
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.security.access_control;zephyr.security.escalation;zephyr.governance;zephyr.integration.mcp
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT]
# [TESTS] tests/test_agent_rbac.py
# [TTL] permanent

import importlib

from zephyr.shared.contracts.identity.agent_identity import (
    MATURITY_AUTO_GUARD_TIMEOUT,
    MATURITY_TLB_LIMITS,
    ROLE_DEFAULT_PERMISSIONS,
    AgentIdentity,
    AgentMaturity,
    AgentRole,
    IDESource,
    MaturityLevel,
)
from zephyr.shared.contracts.identity.permission import GuardDecision, GuardResult


def __getattr__(name):
    if name == "AgentCapability":
        _mod = importlib.import_module("zephyr.governance.agent_spec.registry")
        _AC = _mod.AgentCapability
        globals()["AgentCapability"] = _AC
        return _AC
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "MATURITY_AUTO_GUARD_TIMEOUT",
    "MATURITY_TLB_LIMITS",
    "ROLE_DEFAULT_PERMISSIONS",
    "AgentCapability",
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
