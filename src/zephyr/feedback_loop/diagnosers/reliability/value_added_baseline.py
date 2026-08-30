# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.value_added_baseline
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Value Added Baseline — v0.10.0 R138

Blindspot: No measurement of net value FLE provides vs. baseline automation.
Risk: R138 — FLE costs more than it saves; negative ROI undetected.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: value_added_baseline.py
# 层: 算法
# - id: A1
#   name_zh: ① ValueAddedBaseline
#   name_en: ValueAddedBaseline
#   intro: class ValueAddedBaseline 源码 L55-L61
#   desc: 公共方法（定义序）: roi；源码 L55-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ValueAddedBaseline
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class ValueAddedBaseline:
    cost_baseline: float = 0.0
    cost_fle: float = 0.0

    @property
    def roi(self) -> float:
        return (self.cost_baseline - self.cost_fle) / max(self.cost_fle, 1.0)
