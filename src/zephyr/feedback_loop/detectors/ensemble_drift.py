"""Ensemble Drift — v0.5.0 R43

Blindspot: Ensemble model agreement drifts toward uniformity or chaos.
Risk: R43 — Unanimous agreement masks model monoculture.
"""
from dataclasses import dataclass

@dataclass
class EnsembleDrift:
    agreement_rate: float = 0.0

    def monitor(self, new_rate: float) -> bool:
        drift = abs(new_rate - self.agreement_rate)
        self.agreement_rate = new_rate
        return drift > 0.2
