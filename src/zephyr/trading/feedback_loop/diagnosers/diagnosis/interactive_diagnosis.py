# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.diagnosis.interactive_diagnosis
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-UNK_interactive_diagnosis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Interactive Diagnosis — v0.7.0 R80

Blindspot: One-shot diagnosis cannot handle ambiguous symptoms.
Risk: R80 — Premature diagnosis leads to incorrect repairs.
"""

from dataclasses import dataclass


@dataclass
class InteractiveDiagnosis:
    max_rounds: int = 5

    def probe(self, question: str) -> str:
        return ""
