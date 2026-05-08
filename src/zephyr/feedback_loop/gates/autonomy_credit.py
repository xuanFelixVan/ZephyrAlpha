"""Autonomy Credit System — v0.7.0 R87

Blindspot: No decay of autonomy trust over time.
Risk: R87 — Once-trusted subsystem never re-evaluated.
"""
from dataclasses import dataclass

@dataclass
class AutonomyCredit:
    score: float = 100.0
    decay_per_day: float = 1.0
