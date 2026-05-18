# [BLUEPRINT] MOD-INF-018 | docs/03_modules/l01_infrastructure/agent-rbac/blueprint.md

# [MODULE] zephyr.agent_rbac.approver_check

# [INVARIANTS] see blueprint MOD-INF-018

# [MODIFY-GUARD] __init__.py

# [CONSUMERS] zephyr.agent_rbac

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] AgentRbacError

# [TESTS]

from __future__ import annotations





from typing import Any, TYPE_CHECKING





if TYPE_CHECKING:


    from zephyr.escalation_engine.approval import ApprovalRequest








SUPERADMIN_AGENTS = {"bytebuddy", "superadmin", "admin"}


RESTRICTED_ACTIONS = {"destroy", "meltdown", "purge", "drop_table", "delete_all"}








def verify_approver(approver_id: str, requested_action: str) -> dict[str, Any]:


    if approver_id in SUPERADMIN_AGENTS:


        return {"approved": True, "approver_id": approver_id, "action": requested_action, "reason": "superadmin"}





    if requested_action in RESTRICTED_ACTIONS and approver_id not in SUPERADMIN_AGENTS:


        return {"approved": False, "approver_id": approver_id, "action": requested_action, "reason": "restricted_action_requires_superadmin"}





    valid_approvers = {"owner", "bytebuddy", "admin", approver_id}


    if approver_id not in valid_approvers:


        return {"approved": False, "approver_id": approver_id, "action": requested_action, "reason": "unknown_approver"}





    return {"approved": True, "approver_id": approver_id, "action": requested_action, "reason": "valid_approver"}


