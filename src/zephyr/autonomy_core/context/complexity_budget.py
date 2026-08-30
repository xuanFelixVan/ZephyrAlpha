# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.complexity_budget
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-CONTEXT_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
complexity_budget.py — Token 预算复杂度因子 (DD103, TASK-019)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: complexity_budget.py
# 层: 算法
# - id: A1
#   name_zh: ① ComplexityBudgetAdjuster
#   name_en: ComplexityBudgetAdjuster
#   intro: tree-sitter 复杂度×TaskCard.
#   desc: tree-sitter 复杂度×TaskCard.priority -> budget coefficient (DD103).；公共方法（定义序）: adjust；源码 L59-L68
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ComplexityBudgetAdjuster
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class ComplexityAdjustedBudget:
    base_budget: int
    complexity_factor: float
    adjusted_budget: int


class ComplexityBudgetAdjuster:
    """tree-sitter 复杂度×TaskCard.priority -> budget coefficient (DD103)."""

    def adjust(
        self, base_budget: int = 8000, ast_complexity: int = 10, priority: str = "P2"
    ) -> ComplexityAdjustedBudget:
        factor = 1.0 + (ast_complexity / 100) * (1.0 if priority == "P0" else 0.5)
        return ComplexityAdjustedBudget(
            base_budget=base_budget, complexity_factor=round(factor, 2), adjusted_budget=int(base_budget * factor)
        )
