"""Gamification — v0.8.0 R101

Blindspot: FLE has no positive reinforcement loop for correct diagnoses.
Risk: R101 — Without reward signal, RL-based learning stagnates.
"""
from dataclasses import dataclass


@dataclass
class Gamification:
    score: int = 0
    streak: int = 0

    def reward(self, points: int) -> None:
        self.score += points
        self.streak += 1
