# [BLUEPRINT] MOD-EX-003 | docs/03_modules/_domain_execution_core/audit_journal/blueprint.md
# [MODULE] zephyr.ex_core.audit_journal
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.audit_journal.auditor
# [CONSUMERS] D-REPORTING; D-GOVERNANCE
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_execution_auditor.py
# [A_module] module_id=MOD-EX-003 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


D_EXECUTION_CORE — Execution Audit Journal 包

执行审计记录器模块入口。记录执行事件(E-EX-01~08)的哈希链审计日志。

设计真源: D-EX-CORE-15 Execution Auditor
蓝图: docs/03_modules/_domain_execution_core/audit_journal/blueprint.md

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: auditor 子模块符号 6个
#   fields: AuditChainError / AuditSource / ExecutionAuditEventType / ExecutionAuditLogger / ExecutionAuditRecord / ExecutionAuditReport
#   code: zephyr.ex_core.audit_journal.auditor
# 层: 算法
# - id: A1
#   name_zh: ① 包级聚合再导出
#   name_en: zephyr.ex_core.audit_journal.__init__
#   intro: D_EXECUTION_CORE — Execution Audit Journal 包
#   desc: MOD-EX-003 包入口，包级聚合再导出并声明 __all__（6项）
#   inputs: I1
#   outputs: zephyr.ex_core.audit_journal 包级公共命名空间
#   invariant: 包级导出以 __all__ 声明为准（6项）
# 层: 输出
# - id: O1
#   name_zh: zephyr.ex_core.audit_journal 包公共 API
#   name_en: __all__ 6项
#   intro: D_EXECUTION_CORE — Execution Audit Journal 包——对外统一出口
#   downstream: 见蓝图头 [CONSUMERS] 声明
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# A1 --> O1
"""

from zephyr.ex_core.audit_journal.auditor import (
    AuditChainError,
    AuditSource,
    ExecutionAuditEventType,
    ExecutionAuditLogger,
    ExecutionAuditRecord,
    ExecutionAuditReport,
)

__all__ = [
    "AuditChainError",
    "AuditSource",
    "ExecutionAuditEventType",
    "ExecutionAuditLogger",
    "ExecutionAuditRecord",
    "ExecutionAuditReport",
]
