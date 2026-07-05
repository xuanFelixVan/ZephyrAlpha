# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.evolution.prompt_factory_governance
# [DOMAIN] D_GOVERNANCE
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
# [A_module] module_id=MOD-UNK_prompt_factory_governance | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Prompt Factory Governance — v0.16.0 R224

Blindspot: Prompt templates proliferate without version control; no AB testing of prompt variants.
Risk: R224 — Unversioned prompt changes degrade diagnosis quality; no controlled experiment.

Mitigation: Prompt template factory with versioning, audit trail, and A/B test support.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class PromptVariant:
    variant_id: str
    template_id: str
    version: int
    content: str
    content_hash: str
    created_at: float = field(default_factory=time.time)
    ab_group: str = "control"


@dataclass
class PromptFactoryGovernance:
    variants: dict[str, list[PromptVariant]] = field(default_factory=dict)

    def register(self, template_id: str, content: str) -> PromptVariant:
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:12]
        existing = self.variants.get(template_id, [])
        version = len(existing) + 1
        variant = PromptVariant(
            variant_id=f"{template_id}-v{version}",
            template_id=template_id,
            version=version,
            content=content,
            content_hash=content_hash,
        )
        if template_id not in self.variants:
            self.variants[template_id] = []
        self.variants[template_id].append(variant)
        return variant

    def latest(self, template_id: str) -> PromptVariant | None:
        variants = self.variants.get(template_id, [])
        return variants[-1] if variants else None
