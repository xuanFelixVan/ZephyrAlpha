# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.llm_quality_regression
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
# [A_module] module_id=MOD-UNK_llm_quality_regression | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""LLM Quality Regression — v0.12.0 R161

Blindspot: LLM model updates cause regression in diagnostic quality.
Risk: R161 — New model version produces worse diagnoses than previous.
"""

from dataclasses import dataclass


@dataclass
class LLMQualityRegression:
    previous_accuracy: float = 0.0
    current_accuracy: float = 0.0

    @property
    def regressed(self) -> bool:
        return self.current_accuracy < self.previous_accuracy - 0.05
