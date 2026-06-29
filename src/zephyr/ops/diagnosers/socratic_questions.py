# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.diagnosers.socratic_questions
# [DOMAIN] D_OPS
# [DEPENDENCIES] zephyr.ops.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_socratic_questions | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

"""Socratic Questions — v0.7.0 R81

Blindspot: FLE diagnosis lacks critical self-questioning.
Risk: R81 — Confirmation bias amplifies initial wrong diagnosis.
"""

from dataclasses import dataclass


@dataclass
class SocraticQuestions:
    def generate(self, hypothesis: str) -> list[str]:
        return [
            f"Is {hypothesis} really the root cause?",
            f"What evidence contradicts {hypothesis}?",
            "If deep findings differ from initial diagnosis, why was the initial diagnosis wrong?",
        ]
