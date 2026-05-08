"""Cross-Signal Validator — v0.6.0 R63

Blindspot: Single-signal anomaly may be noise; cross-signal validation missing.
Risk: R63 — Noise spike triggers repair on healthy system.
"""
from dataclasses import dataclass

@dataclass
class CrossSignalValidator:

    def validate(self, primary: float, corroborating: list[float]) -> bool:
        return all(abs(primary - c) < primary * 0.5 for c in corroborating)
