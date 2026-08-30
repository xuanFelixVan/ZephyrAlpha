# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.llm_quality_regression
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
LLM Quality Regression — v0.12.0 R161

Blindspot: LLM model updates cause regression in diagnostic quality.
Risk: R161 — New model version produces worse diagnoses than previous.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: llm_quality_regression.py
# 层: 算法
# - id: A1
#   name_zh: ① LLMQualityRegression
#   name_en: LLMQualityRegression
#   intro: class LLMQualityRegression 源码 L55-L61
#   desc: 公共方法（定义序）: regressed；源码 L55-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: LLMQualityRegression
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class LLMQualityRegression:
    previous_accuracy: float = 0.0
    current_accuracy: float = 0.0

    @property
    def regressed(self) -> bool:
        return self.current_accuracy < self.previous_accuracy - 0.05
