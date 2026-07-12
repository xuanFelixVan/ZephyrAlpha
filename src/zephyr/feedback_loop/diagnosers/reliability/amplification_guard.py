# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.amplification_guard
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_amplification_guard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Amplification Guard — v0.10.0 R134

Blindspot: Multi-hop prompt chains amplify small biases into large errors.
Risk: R134 — Prompt chain amplification causes diagnosis cascade failure.
"""

from dataclasses import dataclass


@dataclass
class AmplificationGuard:
    max_amplification: float = 5.0

    def check(self, input_bias: float, output_bias: float) -> bool:
        return abs(output_bias / max(input_bias, 0.001)) <= self.max_amplification
