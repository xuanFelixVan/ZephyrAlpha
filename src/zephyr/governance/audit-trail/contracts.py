# [BLUEPRINT] MOD-GOV_AUDIT_TRAIL | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.governance.audit_trail.contracts
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.contracts (AuditWriter)
# [CONSUMERS] zephyr.gov_audit.bridge
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] G-CT-002 Audit 契约
# [MODIFY-GUARD] blueprint.md §4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回None
# [TESTS] tests/governance/audit/test_p0_i2_construction_order.py
# [A_module] module_id=MOD-GOV-audit_trail_contracts | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""audit-trail/contracts.py — G-CT-002 Audit 契约（re-export）。"""

from __future__ import annotations

from zephyr.gov_audit.contracts import AuditWriter  # noqa: F401

__all__ = ["AuditWriter"]
