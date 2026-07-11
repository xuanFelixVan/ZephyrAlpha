# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.trading.feedback_loop.verifiers.auto_rollback
# [DOMAIN] D_FBL_VERIFICATION
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-UNK_auto_rollback | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""Auto Rollback — v0.8.0 R93

Blindspot: Bad repair persists; manual rollback required.
Risk: R93 — Harmful repair keeps running because no auto-rollback.
"""

from dataclasses import dataclass


@dataclass
class AutoRollback:
    def should_rollback(self, pre_metric: float, post_metric: float) -> bool:
        return post_metric < pre_metric * 0.7
