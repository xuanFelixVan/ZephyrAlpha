# [A_module] module_id=MOD-INT_approval_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-154 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.approval_types
# [INVARIANTS] 审批请求必须包含完整上下文;审批结果不可伪造
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [CONSUMERS] zephyr.governance.approval; zephyr.security.access_control.approver_check; zephyr.security.access_control.governance_bridges.approver_check
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/governance/test_gct_004_escalation_to_rbac.py; tests/governance/test_p0_u1_contract_smoke.py
"""
G-CT-004 — ApprovalRequest Pydantic V2 BaseModel 审批请求数据结构.
"""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class ApprovalRequest(BaseModel):
    task_id: str
    requested_action: str
    human_approver: str
    reason: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    priority: str = "P2"
    status: str = "PENDING"