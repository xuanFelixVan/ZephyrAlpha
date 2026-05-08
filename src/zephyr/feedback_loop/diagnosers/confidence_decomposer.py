"""Confidence Decomposer — v0.7.0 R83

Blindspot: FLE outputs single confidence score without decomposition.
Risk: R83 — Overconfident on wrong factors despite overall low confidence.
"""
from dataclasses import dataclass


@dataclass
class ConfidenceDecomposer:

    def decompose(self, confidence: float, factors: dict) -> dict:
        return {k: confidence / max(len(factors), 1) for k in factors}
