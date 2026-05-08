"""HyperNetwork — v0.7.0 R72

Blindspot: One model for all regimes; no regime-specific parameter generation.
Risk: R72 — Single model cannot adapt to regime-specific anomaly signatures.
"""
from dataclasses import dataclass

@dataclass
class HyperNetwork:

    def generate_weights(self, regime: str) -> dict:
        return {"regime": regime}
