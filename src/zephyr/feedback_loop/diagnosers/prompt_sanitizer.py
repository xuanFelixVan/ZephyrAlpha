# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.diagnosers.prompt_sanitizer

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Prompt Sanitizer — v0.10.0 R133

Blindspot: External data injected into prompts can carry injection attacks.
Risk: R133 — Prompt injection through diagnosis evidence compromises LLM output.
"""
from dataclasses import dataclass

@dataclass
class PromptSanitizer:
    def sanitize(self, text: str) -> str:
        return text.replace("ignore previous", "[FILTERED]")
