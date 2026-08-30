# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md
# [MODULE] zephyr.infrastructure.capacity_assurance.budget_forecaster
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.capacity_assurance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/budget/test_budget_forecaster.py
# [A_module] module_id=MOD-INF-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# SRC-0041 (P3 迁移恢复, 2026-07-02): 文件从 autonomy_core/budget_forecaster.py 迁移至
#   infrastructure/capacity_assurance/budget_forecaster.py（blueprint actual_disk_path 真源）。
"""
budget_forecaster.py — Token 预算预测 (DD120-extra, TASK-020)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: budget_forecaster.py
# 层: 算法
# - id: A1
#   name_zh: ① BudgetForecaster
#   name_en: BudgetForecaster
#   intro: Historical task token->predict next task budget (machine le…
#   desc: Historical task token->predict next task budget (machine learning approach).；公共方法（定义序）: forecast；源码 L61-L72
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: BudgetForecaster
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

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
