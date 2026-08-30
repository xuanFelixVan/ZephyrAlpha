# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.cognitive.cognitive_load
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
Cognitive Load Estimator — v0.6.0 R68

Blindspot: Owner cognitive bandwidth not modeled — notification flood causes fatigue.
Risk: R68 — 1-person operator overwhelmed, critical alerts missed.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: cognitive_load.py
# 层: 算法
# - id: A1
#   name_zh: ① CognitiveLoad
#   name_en: CognitiveLoad
#   intro: class CognitiveLoad 源码 L55-L61
#   desc: 公共方法（定义序）: update；源码 L55-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: CognitiveLoad
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class CognitiveLoad:
    notifications_per_hour: float = 0.0
    fatigue_score: float = 0.0

    def update(self, new_notifications: int) -> None:
        self.notifications_per_hour = new_notifications
        self.fatigue_score = min(1.0, self.fatigue_score + 0.1 * new_notifications)
