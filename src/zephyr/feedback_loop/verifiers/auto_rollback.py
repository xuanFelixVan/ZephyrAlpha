# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.verifiers.auto_rollback

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Auto Rollback — v0.8.0 R93

Blindspot: Bad repair persists; manual rollback required.
Risk: R93 — Harmful repair keeps running because no auto-rollback.
"""
from dataclasses import dataclass

@dataclass
class AutoRollback:

    def should_rollback(self, pre_metric: float, post_metric: float) -> bool:
        return post_metric < pre_metric * 0.7
