# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.collectors.knowledge_freshness
# [DOMAIN] D_FEEDBACK_LOOP
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
# [A_module] module_id=MOD-UNK_knowledge_freshness | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Knowledge Freshness — v0.5.0 R47

Blindspot: Stale KB entries have same weight as fresh ones.
Risk: R47 — Outdated knowledge misguides current diagnosis.
"""

import time
from dataclasses import dataclass, field


@dataclass
class KnowledgeFreshness:
    entries: dict[str, float] = field(default_factory=dict)

    def score(self, entry_id: str, created_at: float) -> float:
        age_days = (time.time() - created_at) / 86400.0
        return max(0.0, 1.0 - age_days / 90.0)
