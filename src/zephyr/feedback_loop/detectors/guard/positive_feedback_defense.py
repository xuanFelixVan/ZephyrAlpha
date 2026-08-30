# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.guard.positive_feedback_defense
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] zephyr.feedback_loop.detectors.__init__
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
Positive Feedback Defense — v0.4.0 R28

Blindspot: FLE repair triggers metric improvement that triggers new FLE cycle; infinite loop.
Risk: R28 — Positive feedback loop between FLE action and metric causes runaway repairs.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: positive_feedback_defense.py
# 层: 算法
# - id: A1
#   name_zh: ① PositiveFeedbackDefense
#   name_en: PositiveFeedbackDefense
#   intro: class PositiveFeedbackDefense 源码 L55-L62
#   desc: 公共方法（定义序）: detect_loop；源码 L55-L62
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: PositiveFeedbackDefense
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class PositiveFeedbackDefense:
    recent_actions: list[str] = field(default_factory=list)

    def detect_loop(self, action: str) -> bool:
        self.recent_actions.append(action)
        if len(self.recent_actions) > 10:
            self.recent_actions.pop(0)
        return self.recent_actions.count(action) >= 3
