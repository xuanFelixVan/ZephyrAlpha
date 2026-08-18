# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §phase1-gate
# [MODULE] zephyr.governance.budget-enforcer
# [DOMAIN] D_GOV_OPS_RESILIENCE
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# Phase 1 gate marker (kebab-case dir). Implementation in zephyr.governance.financial_governance.budget_enforcement.

"""budget-enforcer — Phase 1 gate marker 包（kebab-case 目录）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 包导入
#   fields: import zephyr.governance.budget-enforcer
#   code: 模块级常量定义
# 层: 算法
# - id: A1
#   name_zh: 阶段标记声明
#   name_en: phase1_marker_declare
#   intro: 仅声明 BUDGET_ENFORCER_PHASE1_MARKER；实现在 financial_governance.budget_enforcement
# 层: 输出
# - id: O1
#   name_zh: 阶段门标记
#   name_en: phase1_marker
#   intro: BUDGET_ENFORCER_PHASE1_MARKER = 'budget-enforcer-v1'
#   downstream: Phase 1 门禁检查
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> O1
"""

BUDGET_ENFORCER_PHASE1_MARKER = "budget-enforcer-v1"

__all__: list[str] = []
