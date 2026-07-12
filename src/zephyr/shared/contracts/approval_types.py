# [BLUEPRINT] SRC-154 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.shared.contracts.approval_types
# [DOMAIN] D_INTEGRATION
# [DEPENDENCIES]
# [CONSUMERS] zephyr.gov_enforcement.rule_enforcement.approval; zephyr.security.access_control.approver_check
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审批请求必须包含完整上下文;审批结果不可伪造
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/governance/test_gct_004_escalation_to_rbac.py; tests/governance/test_p0_u1_contract_smoke.py
# [A_module] module_id=MOD-INT_approval_types | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
G-CT-004 — ApprovalRequest Pydantic V2 BaseModel 审批请求数据结构.
"""

from __future__ import annotations

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
