# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.collectors.market_calendar
# [DOMAIN] D_FEEDBACK_LOOP
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
Market Calendar — v0.5.0 R48

Blindspot: FLE unaware of market holidays; diagnoses no-data as pipeline failure.
Risk: R48 — Holiday false alarms erode trust in FLE.

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: market_calendar.py
# 层: 算法
# - id: A1
#   name_zh: ① MarketCalendar
#   name_en: MarketCalendar
#   intro: class MarketCalendar 源码 L55-L59
#   desc: 公共方法（定义序）: is_trading_day；源码 L55-L59
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（1 定义）
#   name_en: public defs
#   intro: MarketCalendar
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from dataclasses import dataclass, field


@dataclass
class MarketCalendar:
    holidays: set[str] = field(default_factory=set)

    def is_trading_day(self, date_str: str) -> bool:
        return date_str not in self.holidays
