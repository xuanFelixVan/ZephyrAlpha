# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.approval
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.contracts.approval_types
# [CONSUMERS] zephyr.governance.services.adapter
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 审批请求必须包含完整上下文;审批结果不可伪造
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-RES_approval | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-004 — Backward-compat re-export of ApprovalRequest from shared.contracts.approval_types.
"""

from __future__ import annotations

from zephyr.shared.contracts.approval_types import ApprovalRequest  # noqa: F401 — re-export
