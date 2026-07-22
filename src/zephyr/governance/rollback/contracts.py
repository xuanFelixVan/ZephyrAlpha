# [BLUEPRINT] MOD-GOV_ROLLBACK | docs/03_modules/_domain_governance/rollback/blueprint.md | §
# [MODULE] zephyr.governance.rollback.contracts
# [DOMAIN] D_INFRA_RECOVERY
# [DEPENDENCIES] zephyr.infrastructure.rollback.contracts (RollbackHandler)
# [CONSUMERS] zephyr.gov_audit.bridge
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] G-CT-002 Rollback 契约
# [MODIFY-GUARD] blueprint.md §4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回None
# [TESTS] tests/governance/audit/test_p0_i2_construction_order.py
# [A_module] module_id=MOD-GOV-rollback_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""rollback/contracts.py — G-CT-002 Rollback 契约（re-export）。"""

from __future__ import annotations

from zephyr.infrastructure.rollback.contracts import RollbackHandler  # noqa: F401

__all__ = ["RollbackHandler"]
