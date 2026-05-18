# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md

# [MODULE] zephyr.agent_rbac.bootstrap_superadmin

# [INVARIANTS] see blueprint MOD-INF-018

# [MODIFY-GUARD] __init__.py

# [CONSUMERS] zephyr.agent_rbac

# [STABILITY] stable

# [SAFETY] M

# [AI_AUTONOMY] human_gated

# [ERROR_CONTRACT] AgentRbacError

# [TESTS]

from __future__ import annotations





from typing import Any





SUPERADMIN_ACCOUNT = "bytebuddy"


SUPERADMIN_ROLES = ["bootstrap", "superadmin", "admin", "auditor"]


SUPERADMIN_CAPABILITIES = ["read", "write", "execute", "deploy", "audit", "escalate", "rollback"]








class BootstrapSuperadmin:





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


