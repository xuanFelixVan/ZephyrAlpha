# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.actors.alert_router

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Alert Router — v0.3.0 R13

Blindspot: All alerts go to single channel; no routing based on severity/type.
Risk: R13 — Critical alert buried in low-priority notifications.
"""
from dataclasses import dataclass

@dataclass
class AlertRouter:

    def route(self, severity: int) -> str:
        if severity >= 8:
            return "PAGERDUTY"
        if severity >= 5:
            return "SLACK"
        return "EMAIL"
