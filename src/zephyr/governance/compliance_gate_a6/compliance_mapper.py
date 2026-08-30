# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.governance.compliance_gate_a6.compliance_mapper
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS] zephyr.infrastructure.escalation
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 合规映射必须同步法律变更;blocked操作必须同步确认
# [MODIFY-GUARD] docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Compliance Mapper — D-022-13 合规映射器: 操作->法规(SOX/GDPR/MiFID)映射+审计迹。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: compliance_mapper.py
# 层: 算法
# - id: A1
#   name_zh: ① ComplianceMapper
#   name_en: ComplianceMapper
#   intro: class ComplianceMapper 源码 L60-L66
#   desc: 公共方法（定义序）: check, requires_escalation；源码 L60-L66
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ComplianceMapper
#   downstream: zephyr.infrastructure.escalation
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
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
