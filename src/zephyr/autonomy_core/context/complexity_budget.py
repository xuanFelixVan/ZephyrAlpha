# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context-engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.complexity_budget
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
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
# [A_module] module_id=MOD-ORC_complexity_budget | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""complexity_budget.py — Token 预算复杂度因子 (DD103, TASK-019)"""

from dataclasses import dataclass


@dataclass
class ComplexityAdjustedBudget:
    base_budget: int
    complexity_factor: float
    adjusted_budget: int


class ComplexityBudgetAdjuster:
    """tree-sitter 复杂度×TaskCard.priority → budget coefficient (DD103)."""

    def adjust(
        self, base_budget: int = 8000, ast_complexity: int = 10, priority: str = "P2"
    ) -> ComplexityAdjustedBudget:
        factor = 1.0 + (ast_complexity / 100) * (1.0 if priority == "P0" else 0.5)
        return ComplexityAdjustedBudget(
            base_budget=base_budget, complexity_factor=round(factor, 2), adjusted_budget=int(base_budget * factor)
        )
