# [A_module] module_id=MOD-UNK_cross_signal_validator | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.detectors.cross_signal_validator

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] M

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Cross-Signal Validator — v0.6.0 R63

Blindspot: Single-signal anomaly may be noise; cross-signal validation missing.
Risk: R63 — Noise spike triggers repair on healthy system.
"""

from dataclasses import dataclass


@dataclass
class CrossSignalValidator:
    def validate(self, primary: float, corroborating: list[float]) -> bool:
        return all(abs(primary - c) < primary * 0.5 for c in corroborating)
