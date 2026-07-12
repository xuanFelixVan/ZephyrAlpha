# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.feedback_loop.diagnosers.reliability.context_truncation
# [DOMAIN] D_FEEDBACK_LOOP
# [DEPENDENCIES] zephyr.feedback_loop.diagnosers.__init__
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
# [A_module] module_id=MOD-UNK_context_truncation | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Context Truncation Detector — v0.9.0 R122

Blindspot: LLM context window overflow silently drops critical diagnostic evidence.
Risk: R122 — Truncated context causes misdiagnosis on complex multi-factor anomalies.
"""

from dataclasses import dataclass


@dataclass
class ContextTruncation:
    max_tokens: int = 8192

    def check(self, token_count: int) -> bool:
        return token_count > self.max_tokens
