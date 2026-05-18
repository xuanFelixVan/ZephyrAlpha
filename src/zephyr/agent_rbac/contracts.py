# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md

# [MODULE] zephyr.agent_rbac.contracts

# [INVARIANTS] audit records must be immutable after write

# [MODIFY-GUARD] permission_guard.py; __init__.py

# [CONSUMERS] zephyr.agent_rbac.permission_guard; zephyr.audit_trail

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] AgentRbacError

# [TESTS] tests/agent_rbac/test_integration.py

from __future__ import annotations





from datetime import datetime, timezone


from typing import Any





from zephyr.audit_trail.contracts import AuditWriter








class RBACAuditBridge:





    def __init__(self) -> None:


        self._audit = AuditWriter()





    def check_and_log(


        self,


        agent_id: str,


        permission: str,


        resource: str,


        session_id: str = "",


    ) -> dict[str, Any]:


        granted = self._check_permission(agent_id, permission, resource)





        decision_basis = (


            f"RBAC: agent={agent_id} perm={permission} res={resource}"


        )





        record = self._audit.write(


            agent_id=agent_id,


            permission=permission,


            resource=resource,


            decision_basis=decision_basis,


            timestamp=datetime.now(timezone.utc).isoformat(),


            session_id=session_id,


            granted=granted,


        )





        return {


            "granted": granted,


            "audit_record": record,


        }





    @staticmethod


    def _check_permission(agent_id: str, permission: str, resource: str) -> bool:


        allowed_permissions = {"read", "write", "execute"}


        return permission in allowed_permissions


