# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.no_llm_degradation
# [DOMAIN] D_FBL_VERIFICATION
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
# [A_module] module_id=MOD-UNK_no_llm_degradation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""No-LLM Degradation Mode — v0.8.0 R94

Blindspot: LLM outage paralyses FLE.
Risk: R94 — LLM API down; FLE cannot diagnose or repair anything.
"""

from dataclasses import dataclass


@dataclass
class NoLLMDegradation:
    rules_engine_active: bool = False
