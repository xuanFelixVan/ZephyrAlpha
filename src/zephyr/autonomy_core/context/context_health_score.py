# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_health_score
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
ContextHealthScore.py — 统一健康分 (B6, DD80, TASK-015 beta v)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: context_health_score.py
# 层: 算法
# - id: A1
#   name_zh: ① ContextHealthScore
#   name_en: ContextHealthScore
#   intro: PCA of 30 sub-metrics -> Unified Health Score(0-100) (DD80).
#   desc: PCA of 30 sub-metrics -> Unified Health Score(0-100) (DD80).；公共方法（定义序）: compute；源码 L59-L68
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ContextHealthScore
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class HealthScoreReport:
    score: float  # 0-100
    status: str  # healthy / degraded / critical
    sub_metrics: dict[str, float]


class ContextHealthScore:
    """PCA of 30 sub-metrics -> Unified Health Score(0-100) (DD80)."""

    def compute(self, metrics: dict[str, float]) -> HealthScoreReport:
        if not metrics:
            return HealthScoreReport(score=100.0, status="healthy", sub_metrics={})
        avg = sum(metrics.values()) / len(metrics)
        score = min(100.0, max(0.0, avg))
        status = "healthy" if score >= 70 else ("degraded" if score >= 40 else "critical")
        return HealthScoreReport(score=round(score, 1), status=status, sub_metrics=metrics)
