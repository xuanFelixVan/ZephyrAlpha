# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.compliance_gate_a6.compliance_mapper
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 合规映射必须同步法律变更;blocked操作必须同步确认
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_compliance_mapper | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Compliance Mapper — D-022-13 合规映射器: 操作→法规(SOX/GDPR/MiFID)映射+审计迹。
"""

from __future__ import annotations

from typing import Final
COMPLIANCE_MAP: Final[set] = {
    "modify_financial_data": {"sox": True, "gdpr": False, "mifid": True},
    "access_personal_data": {"sox": False, "gdpr": True, "mifid": False},
    "execute_trade": {"sox": True, "gdpr": False, "mifid": True},
    "delete_audit_log": {"sox": True, "gdpr": False, "mifid": True},
}


class ComplianceMapper:
    def check(self, operation: str) -> dict:
        return COMPLIANCE_MAP.get(operation, {"sox": False, "gdpr": False, "mifid": False})

    def requires_escalation(self, operation: str) -> bool:
        check = self.check(operation)
        return any(check.values())
