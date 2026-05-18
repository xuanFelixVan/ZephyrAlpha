# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.verifiers.sim2real_calibration

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Sim2Real Calibration — v0.6.0 R56

Blindspot: Simulation accuracy degrades without recalibration.
Risk: R56 — Simulated repair success rate diverges from real success rate.
"""
from dataclasses import dataclass

@dataclass
class Sim2RealCalibration:
    sim_accuracy: float = 0.0
    real_accuracy: float = 0.0

    @property
    def gap(self) -> float:
        return abs(self.sim_accuracy - self.real_accuracy)
