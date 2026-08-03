# [BLUEPRINT] MOD-GOV_AGENT_RBAC | docs/03_modules/_domain_autonomy_core/agent_role_based_access_control/blueprint.md | §
# [MODULE] zephyr.governance.agent_rbac.contracts
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.contracts (RBACAuditBridge)
# [CONSUMERS] tests.governance.test_p0_i2_construction_order
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] G-CT-001 RBAC 契约
# [MODIFY-GUARD] blueprint.md §4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回None
# [TESTS] tests/governance/audit/test_p0_i2_construction_order.py
# [A_module] module_id=MOD-GOV_AGENT_RBAC | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""agent-rbac/contracts.py — G-CT-001 RBAC 契约（re-export）。"""

from __future__ import annotations

from zephyr.security.access_control.contracts import RBACAuditBridge  # noqa: F401

__all__ = ["RBACAuditBridge"]
