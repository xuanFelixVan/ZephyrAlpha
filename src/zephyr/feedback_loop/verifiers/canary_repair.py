"""Canary Repair — v0.8.0 R104b

Blindspot: Repairs deployed to all instances simultaneously.
Risk: R104b — Bad repair affects 100% of instances instantly.
"""
from dataclasses import dataclass

@dataclass
class CanaryRepair:
    canary_pct: float = 0.1
