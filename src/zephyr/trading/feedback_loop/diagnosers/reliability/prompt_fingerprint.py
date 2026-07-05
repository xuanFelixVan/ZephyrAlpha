# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.diagnosers.reliability.prompt_fingerprint
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
# [A_module] module_id=MOD-UNK_prompt_fingerprint | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Prompt Fingerprint — v0.3.0 R14

Blindspot: LLM prompts drift silently over time without version tracking.
Risk: R14 — Prompt drift causes diagnostic inconsistency across sessions.
"""

import hashlib
from dataclasses import dataclass


@dataclass
class PromptFingerprint:
    prompt_id: str
    content_hash: str = ""

    @classmethod
    def from_content(cls, prompt_id: str, content: str) -> "PromptFingerprint":
        return cls(prompt_id=prompt_id, content_hash=hashlib.sha256(content.encode()).hexdigest())
