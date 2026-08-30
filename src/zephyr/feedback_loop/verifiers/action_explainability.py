# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.verifiers.action_explainability
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES]
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
Action Explainability — v0.3.0 R15

Blindspot: FLE actions opaque; owner cannot understand why a repair was chosen.
Risk: R15 — Trust eroded; owner overrides correct repairs due to lack of explainability.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: action_explainability.py
# 层: 算法
# - id: A1
#   name_zh: ① ActionExplainability
#   name_en: ActionExplainability
#   intro: class ActionExplainability 源码 L55-L57
#   desc: 公共方法（定义序）: explain；源码 L55-L57
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: ActionExplainability
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class ActionExplainability:
    def explain(self, action: dict) -> str:
        return f"Action: {action.get('type')} — Reason: {action.get('reason')}"
