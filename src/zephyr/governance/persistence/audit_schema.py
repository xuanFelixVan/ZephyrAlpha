# 代理模块：将 zephyr.governance.persistence.audit_schema 重定向到 zephyr.governance.audit_schema
from zephyr.governance.audit_schema import AuditQuery

__all__ = ["AuditQuery"]
