# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.market_calendar
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_market_calendar | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Market Calendar — v0.5.0 R48

Blindspot: FLE unaware of market holidays; diagnoses no-data as pipeline failure.
Risk: R48 — Holiday false alarms erode trust in FLE.
"""

from dataclasses import dataclass, field


@dataclass
class MarketCalendar:
    holidays: set[str] = field(default_factory=set)

    def is_trading_day(self, date_str: str) -> bool:
        return date_str not in self.holidays
