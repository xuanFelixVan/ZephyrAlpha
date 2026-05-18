# [BLUEPRINT] MOD-INF-010 | 03_modules/_cross_layer/feedback-loop/blueprint.md | §

# [MODULE] zephyr.feedback_loop.evolution.auto_reward

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""Auto Reward — v0.7.0 R76

Blindspot: RL reward signal requires manual labeling.
Risk: R76 — Without auto-reward, RL learning stalls.
"""
from dataclasses import dataclass

@dataclass
class AutoReward:

    def compute(self, pre_state: float, post_state: float) -> float:
        return post_state - pre_state
