# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.burnout_alarm
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
Burnout Alarm — v0.8.0 R100

Blindspot: 1-person operator burnout undetected until system failure.
Risk: R100 — Owner fatigue causes missed critical alerts and delayed responses.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: burnout_alarm.py
# 层: 算法
# - id: A1
#   name_zh: ① BurnoutAlarm
#   name_en: BurnoutAlarm
#   intro: class BurnoutAlarm 源码 L55-L61
#   desc: 公共方法（定义序）: alarm；源码 L55-L61
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: BurnoutAlarm
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass


@dataclass
class BurnoutAlarm:
    response_latency_avg: float = 0.0
    skip_rate: float = 0.0

    @property
    def alarm(self) -> bool:
        return self.response_latency_avg > 3600.0 or self.skip_rate > 0.3
