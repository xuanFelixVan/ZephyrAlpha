# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [MODULE] zephyr.governance.governance.approval
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_approval | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""G-CT-004 — ApprovalRequest Pydantic V2 BaseModel 审批请求数据结构."""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class ApprovalRequest(BaseModel):
    task_id: str
    requested_action: str
    human_approver: str
    reason: str
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    priority: str = "P2"
    status: str = "PENDING"
