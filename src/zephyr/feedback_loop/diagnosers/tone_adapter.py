# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.diagnosers.tone_adapter

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Tone Adapter — v0.9.0 R127

Blindspot: FLE notification tone static regardless of severity or owner state.
Risk: R127 — Wrong tone causes owner to ignore critical alerts.
"""
from dataclasses import dataclass

@dataclass
class ToneAdapter:
    severity: int = 0

    def adapt(self, severity: int, owner_fatigue: float) -> str:
        return "urgent" if severity > 7 else "standard"
