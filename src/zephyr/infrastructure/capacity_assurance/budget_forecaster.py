# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.budget_forecaster
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/budget/test_budget_forecaster.py
# [A_module] module_id=MOD-INF-001_budget_forecaster | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# SRC-0041 (P3 迁移恢复, 2026-07-02): 文件从 autonomy_core/budget_forecaster.py 迁移至
#   infrastructure/capacity_assurance/budget_forecaster.py（blueprint actual_disk_path 真源）。
"""budget_forecaster.py — Token 预算预测 (DD120-extra, TASK-020)"""

from dataclasses import dataclass


@dataclass
class BudgetForecast:
    session_id: str
    estimated_peak_tokens: int
    recommended_budget: int
    confidence: float  # 0-1


class BudgetForecaster:
    """Historical task token->predict next task budget (machine learning approach)."""

    def forecast(self, session_id: str, task_type: str, prev_token_usages: list[int]) -> BudgetForecast:
        avg = sum(prev_token_usages) / max(1, len(prev_token_usages))
        recommended = int(avg * 1.2) if prev_token_usages else 8000
        return BudgetForecast(
            session_id=session_id,
            estimated_peak_tokens=max(prev_token_usages) if prev_token_usages else 8000,
            recommended_budget=recommended,
            confidence=0.75,
        )
