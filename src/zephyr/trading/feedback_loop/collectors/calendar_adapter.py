# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.calendar_adapter
# [DOMAIN] D_OPS
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
# [A_module] module_id=MOD-UNK_calendar_adapter | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Calendar Adapter — v0.8.0 R102b

Blindspot: FLE operates same way during weekends as weekdays.
Risk: R102b — Weekend low-urgency repairs escalate unnecessarily.
"""

from dataclasses import dataclass


@dataclass
class CalendarAdapter:
    is_weekend: bool = False
