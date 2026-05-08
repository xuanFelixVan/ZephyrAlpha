"""Phase 1 Gate — bytebuddy 超管角色伪实现 硬编码单个超管 account."""
from __future__ import annotations

from typing import Any

SUPERADMIN_ACCOUNT = "bytebuddy"
SUPERADMIN_ROLES = ["bootstrap", "superadmin", "admin", "auditor"]
SUPERADMIN_CAPABILITIES = ["read", "write", "execute", "deploy", "audit", "escalate", "rollback"]


class BootstrapSuperadmin:
    """Phase 1 超管角色伪实现 — 无需数据库."""

    def __init__(self) -> None:
        self.account_id = SUPERADMIN_ACCOUNT
        self.roles = SUPERADMIN_ROLES
        self.capabilities = SUPERADMIN_CAPABILITIES

    def check(self, permission: str, resource: str) -> dict[str, Any]:
        if permission in self.capabilities:
            return {"granted": True, "agent_id": self.account_id, "permission": permission, "resource": resource, "role": "superadmin"}
        return {"granted": False, "agent_id": self.account_id, "permission": permission, "resource": resource, "reason": "capability_not_granted"}

    def bootstrap(self) -> dict[str, Any]:
        return {"bootstrapped": True, "account": self.account_id, "roles": self.roles, "capabilities": self.capabilities}
