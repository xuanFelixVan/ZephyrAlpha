# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.governance.persistence.audit_schema
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit_schema
# [CONSUMERS] zephyr.governance.database_manager; tests.unit.test_audit_schema_unit; tests.unit.db.test_audit_schema_db
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] task_bound
# 代理模块：将 zephyr.governance.persistence.audit_schema 重定向到 zephyr.governance.audit_schema
from zephyr.governance.audit_schema import AuditQuery

__all__ = ["AuditQuery"]
