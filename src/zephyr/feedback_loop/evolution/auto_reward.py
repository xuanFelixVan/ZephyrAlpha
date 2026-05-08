"""Auto Reward — v0.7.0 R76

Blindspot: RL reward signal requires manual labeling.
Risk: R76 — Without auto-reward, RL learning stalls.
"""
from dataclasses import dataclass

@dataclass
class AutoReward:

    def compute(self, pre_state: float, post_state: float) -> float:
        return post_state - pre_state
