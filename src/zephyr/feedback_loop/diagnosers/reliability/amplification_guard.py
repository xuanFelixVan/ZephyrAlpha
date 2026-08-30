# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.amplification_guard
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
Amplification Guard — v0.10.0 R134

Blindspot: Multi-hop prompt chains amplify small biases into large errors.
Risk: R134 — Prompt chain amplification causes diagnosis cascade failure.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: amplification_guard.py
# 层: 算法
# - id: A1
#   name_zh: ① AmplificationGuard
#   name_en: AmplificationGuard
#   intro: class AmplificationGuard 源码 L55-L59
#   desc: 公共方法（定义序）: check；源码 L55-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: AmplificationGuard
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class AmplificationGuard:
    max_amplification: float = 5.0

    def check(self, input_bias: float, output_bias: float) -> bool:
        return abs(output_bias / max(input_bias, 0.001)) <= self.max_amplification
