"""Meta Performance Gate — v0.11.0 R158

Blindspot: FLE performance evaluated only externally; internal benchmark invisible.
"""
from dataclasses import dataclass

@dataclass
class MetaPerformanceGate:
    mttd_seconds: float = 300.0
    mttr_seconds: float = 600.0
