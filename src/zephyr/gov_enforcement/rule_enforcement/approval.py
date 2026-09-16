# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md
# [MODULE] zephyr.gov_enforcement.rule_enforcement.approval
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.shared.contracts.approval_types
# [CONSUMERS] zephyr.governance.services.adapter
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审批请求必须包含完整上下文;审批结果不可伪造
# [MODIFY-GUARD] docs/03_modules/_domain-autonomy_perm/escalation-protocol/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 异常必须包含 context 和 rule_id
# [TESTS] tests/e/test_e_gov_approval.py; tests/escalation/test_escalation_gov_approval.py; tests/governance/access_control/test_approval.py; tests/governance/security/test_gct_004_escalation_to_rbac.py; tests/governance/security/test_p0_u1_contract_smoke.py  # 2026-09-05 STEWARD B20 重锚：AI-00 修复脚本 src. 前缀 bug 漏网（AST/patch 直查 5 个测试）
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-004 — Backward-compat re-export of ApprovalRequest from shared.contracts.approval_types.

# [ALGO_FLOW] external: docs/03_modules/_domain_gov_enforcement/algo_flow/rule_enforcement/approval.yaml
"""

from __future__ import annotations

from zephyr.shared.contracts.approval_types import ApprovalRequest  # noqa: F401 — re-export
