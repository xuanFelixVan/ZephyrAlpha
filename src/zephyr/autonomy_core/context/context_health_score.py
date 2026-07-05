# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_health_score
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
# [A_module] module_id=MOD-ORC_context_health_score | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""ContextHealthScore.py — 统一健康分 (B6, DD80, TASK-015 beta v)"""

from dataclasses import dataclass


@dataclass
class HealthScoreReport:
    score: float  # 0-100
    status: str  # healthy / degraded / critical
    sub_metrics: dict[str, float]


class ContextHealthScore:
    """PCA of 30 sub-metrics → Unified Health Score(0-100) (DD80)."""

    def compute(self, metrics: dict[str, float]) -> HealthScoreReport:
        if not metrics:
            return HealthScoreReport(score=100.0, status="healthy", sub_metrics={})
        avg = sum(metrics.values()) / len(metrics)
        score = min(100.0, max(0.0, avg))
        status = "healthy" if score >= 70 else ("degraded" if score >= 40 else "critical")
        return HealthScoreReport(score=round(score, 1), status=status, sub_metrics=metrics)
