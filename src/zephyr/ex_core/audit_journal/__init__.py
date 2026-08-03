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
"""D_EXECUTION_CORE — Execution Audit Journal 包

执行审计记录器模块入口。记录执行事件(E-EX-01~08)的哈希链审计日志。

设计真源: D-EX-CORE-15 Execution Auditor
蓝图: docs/03_modules/_domain_execution_core/audit_journal/blueprint.md
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
