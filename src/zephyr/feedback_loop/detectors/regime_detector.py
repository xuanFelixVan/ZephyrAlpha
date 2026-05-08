"""Regime Detector — v0.5.0 R49

Blindspot: Market regime changes invisible to FLE; normal-vol diagnoses applied in crisis.
Risk: R49 — Crisis-mode diagnosis logic identical to normal; catastrophic false negatives.
"""
from dataclasses import dataclass

@dataclass
class RegimeDetector:
    current_regime: str = "NORMAL"

    def detect(self, volatility: float) -> str:
        if volatility > 3.0:
            return "CRISIS"
        if volatility > 1.5:
            return "ELEVATED"
        return "NORMAL"
