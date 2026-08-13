# [BLUEPRINT] MOD-GOV_AUDIT_TRAIL | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] zephyr.governance.audit_trail.contracts
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.gov_audit.contracts (AuditWriter)
# [CONSUMERS] zephyr.gov_audit.bridge
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] G-CT-002 Audit 契约
# [MODIFY-GUARD] blueprint.md §4
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 桥接失败返回None
# [TESTS] tests/governance/audit/test_p0_i2_construction_order.py
# [A_module] module_id=MOD-GOV_AUDIT_TRAIL | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

audit-trail/contracts.py — G-CT-002 Audit 契约（re-export）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: AuditWriter 审计写入契约 类定义
#   fields: zephyr.gov_audit.contracts.AuditWriter（G-CT-002 Audit 契约）
#   code: from zephyr.gov_audit.contracts import AuditWriter L21
# 层: 算法
# - id: A1
#   name_zh: ① 契约再导出
#   name_en: re-export AuditWriter
#   intro: 把 AuditWriter 从 gov_audit.contracts 原样再导出，作为 audit-trail 域的统一入口
#   desc: 单行 import + __all__=["AuditWriter"]，无包装无逻辑；桥接失败返回 None
#   inputs: I1
#   outputs: AuditWriter 符号
# 层: 输出
# - id: O1
#   name_zh: G-CT-002 Audit 契约符号
#   name_en: AuditWriter
#   intro: 审计写入契约的统一引用点，保证 audit-trail 域与 gov_audit 同源
#   downstream: zephyr.gov_audit.bridge（[CONSUMERS]）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.gov_audit.contracts import AuditWriter  # noqa: F401

__all__ = ["AuditWriter"]
