# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.detectors.capacity_forecast

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Capacity Forecast — v0.13.0 R186b

Blindspot: Resource exhaustion predicted days in advance; no proactive alert.
"""
from dataclasses import dataclass

@dataclass
class CapacityForecast:
    days_until_full: float = float("inf")
