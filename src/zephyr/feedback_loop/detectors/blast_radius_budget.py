"""Blast Radius Budget — v0.13.0 R178

Blindspot: No constraint on maximum simultaneous repair scope.
Risk: R178 — Simultaneous repairs across all subsystems; if wrong, total collapse.
"""
from dataclasses import dataclass

@dataclass
class BlastRadiusBudget:
    max_concurrent_repairs: int = 3
    active_repairs: int = 0
