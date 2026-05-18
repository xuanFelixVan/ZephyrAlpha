# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.diagnosers.prompt_fingerprint

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Prompt Fingerprint — v0.3.0 R14

Blindspot: LLM prompts drift silently over time without version tracking.
Risk: R14 — Prompt drift causes diagnostic inconsistency across sessions.
"""
from dataclasses import dataclass
import hashlib


@dataclass
class PromptFingerprint:
    prompt_id: str
    content_hash: str = ""

    @classmethod
    def from_content(cls, prompt_id: str, content: str) -> "PromptFingerprint":
        return cls(prompt_id=prompt_id, content_hash=hashlib.sha256(content.encode()).hexdigest())
