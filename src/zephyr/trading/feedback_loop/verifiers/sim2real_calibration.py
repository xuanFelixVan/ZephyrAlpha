# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.sim2real_calibration
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
# [A_module] module_id=MOD-UNK_sim2real_calibration | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

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
