# [BLUEPRINT] MOD-INF-008 | 03_modules/_cross_layer/context-engine/blueprint.md | §

# [MODULE] zephyr.context_engine.complexity_budget

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""complexity_budget.py — Token 预算复杂度因子 (DD103, TASK-019)"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ComplexityAdjustedBudget:
    base_budget: int
    complexity_factor: float
    adjusted_budget: int


class ComplexityBudgetAdjuster:
    """tree-sitter 复杂度×TaskCard.priority → budget coefficient (DD103)."""
    def adjust(self, base_budget: int = 8000, ast_complexity: int = 10, priority: str = "P2") -> ComplexityAdjustedBudget:
        factor = 1.0 + (ast_complexity / 100) * (1.0 if priority == "P0" else 0.5)
        return ComplexityAdjustedBudget(base_budget=base_budget, complexity_factor=round(factor, 2), adjusted_budget=int(base_budget * factor))
