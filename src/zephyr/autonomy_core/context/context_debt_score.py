# [BLUEPRINT] MOD-CONTEXT_ENGINE | docs/03_modules/_cross_layer/context_engine/blueprint.md
# [MODULE] zephyr.autonomy_core.context.context_debt_score
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
context_debt_score.py — 上下文债务评分 (B19, DD93, TASK-017)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: context_debt_score.py
# 层: 算法
# - id: A1
#   name_zh: ① ContextDebtScorer
#   name_en: ContextDebtScorer
#   intro: per-KE deprecation_risk = age * conflict * ref_staleness; >…
#   desc: per-KE deprecation_risk = age * conflict * ref_staleness; >0.7 -> [DEPRECATED] (DD93).；公共方法（定义序）: score；源码 L6…
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: ContextDebtScorer
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class DebtScore:
    ke_id: str
    age_days: float
    conflict_count: int
    ref_staleness: float
    deprecation_risk: float
    deprecated: bool


class ContextDebtScorer:
    """per-KE deprecation_risk = age * conflict * ref_staleness; >0.7 -> [DEPRECATED] (DD93)."""

    def score(self, ke_id: str, age_days: float, conflict_count: int, ref_staleness: float) -> DebtScore:
        risk = (age_days / 365) * max(1, conflict_count) * max(0.1, ref_staleness)
        risk_clamped = min(1.0, risk)
        return DebtScore(
            ke_id=ke_id,
            age_days=age_days,
            conflict_count=conflict_count,
            ref_staleness=ref_staleness,
            deprecation_risk=round(risk_clamped, 3),
            deprecated=risk_clamped > 0.7,
        )
