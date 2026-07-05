# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.burnout_alarm
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.trading.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_burnout_alarm | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Burnout Alarm — v0.8.0 R100

Blindspot: 1-person operator burnout undetected until system failure.
Risk: R100 — Owner fatigue causes missed critical alerts and delayed responses.
"""

from dataclasses import dataclass


@dataclass
class BurnoutAlarm:
    response_latency_avg: float = 0.0
    skip_rate: float = 0.0

    @property
    def alarm(self) -> bool:
        return self.response_latency_avg > 3600.0 or self.skip_rate > 0.3
