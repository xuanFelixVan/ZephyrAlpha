# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.detectors.ensemble_drift

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Ensemble Drift — v0.5.0 R43

Blindspot: Ensemble model agreement drifts toward uniformity or chaos.
Risk: R43 — Unanimous agreement masks model monoculture.
"""
from dataclasses import dataclass

@dataclass
class EnsembleDrift:
    agreement_rate: float = 0.0

    def monitor(self, new_rate: float) -> bool:
        drift = abs(new_rate - self.agreement_rate)
        self.agreement_rate = new_rate
        return drift > 0.2
