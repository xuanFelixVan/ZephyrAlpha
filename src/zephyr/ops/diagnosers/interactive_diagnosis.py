# [A_module] module_id=MOD-UNK_interactive_diagnosis | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md

# [MODULE] zephyr.observability.feedback_loop.diagnosers.interactive_diagnosis

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

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
