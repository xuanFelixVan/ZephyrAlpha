# [BLUEPRINT] MOD-INF-010 | docs/03_modules/_cross_layer/feedback-loop/blueprint.md
# [MODULE] zephyr.observability.feedback_loop.evolution.auto_reward
# [DOMAIN] D-OPS
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
# [A_module] module_id=MOD-UNK_auto_reward | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""Auto Reward — v0.7.0 R76

Blindspot: RL reward signal requires manual labeling.
Risk: R76 — Without auto-reward, RL learning stalls.
"""

from dataclasses import dataclass


@dataclass
class AutoReward:
    def compute(self, pre_state: float, post_state: float) -> float:
        return post_state - pre_state
