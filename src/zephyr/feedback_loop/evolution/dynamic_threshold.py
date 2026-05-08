"""Dynamic Threshold — v0.7.0 R71

Blindspot: Static anomaly thresholds break under regime change.
Risk: R71 — Threshold too tight in high vol; too loose in low vol.
"""
from dataclasses import dataclass

@dataclass
class DynamicThreshold:
    base: float = 2.5
    current: float = 2.5
