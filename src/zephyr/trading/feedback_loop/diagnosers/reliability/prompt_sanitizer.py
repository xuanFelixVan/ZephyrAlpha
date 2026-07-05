# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.prompt_sanitizer
# [DOMAIN] D_OPS
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
# [A_module] module_id=MOD-UNK_prompt_sanitizer | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Prompt Sanitizer — v0.10.0 R133

Blindspot: External data injected into prompts can carry injection attacks.
Risk: R133 — Prompt injection through diagnosis evidence compromises LLM output.
"""

from dataclasses import dataclass


@dataclass
class PromptSanitizer:
    def sanitize(self, text: str) -> str:
        return text.replace("ignore previous", "[FILTERED]")
