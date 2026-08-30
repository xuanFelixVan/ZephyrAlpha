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
# [TESTS] tests/test_escalation_engine.py
# [A_module] module_id=MOD-INF-022 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
G-CT-004 — Backward-compat re-export of ApprovalRequest from shared.contracts.approval_types.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: approval.py
# 层: 算法
# - id: A1
#   name_zh: ① 模块占位（无公共定义）
#   name_en: placeholder
#   intro: approval.py 无顶层公共函数/类/再导出（AST 事实）
#   desc: 源码 L1-L50；包结构占位或纯内部模块
#   inputs: I1
#   outputs: 无（占位）
# 层: 输出
# - id: O1
#   name_zh: 无输出（占位模块）
#   name_en: none
#   intro: 无公共定义无再导出（AST 事实）
#   downstream: zephyr.governance.services.adapter
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

from zephyr.shared.contracts.approval_types import ApprovalRequest  # noqa: F401 — re-export
