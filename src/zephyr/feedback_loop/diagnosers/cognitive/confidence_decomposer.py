# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive.confidence_decomposer
# [DOMAIN] D_FBL_DIAGNOSERS
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-FEEDBACK_LOOP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Confidence Decomposer — v0.7.0 R83

Blindspot: FLE outputs single confidence score without decomposition.
Risk: R83 — Overconfident on wrong factors despite overall low confidence.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: confidence_decomposer.py
# 层: 算法
# - id: A1
#   name_zh: ① ConfidenceDecomposer
#   name_en: ConfidenceDecomposer
#   intro: class ConfidenceDecomposer 源码 L55-L57
#   desc: 公共方法（定义序）: decompose；源码 L55-L57
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ConfidenceDecomposer
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class ConfidenceDecomposer:
    def decompose(self, confidence: float, factors: dict) -> dict:
        return {k: confidence / max(len(factors), 1) for k in factors}
