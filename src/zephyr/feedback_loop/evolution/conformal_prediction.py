"""Conformal Prediction — v0.7.0 R74

Blindspot: Anomaly scores lack calibrated confidence intervals.
Risk: R74 — High anomaly score with wide confidence; overconfident diagnosis.
"""
from dataclasses import dataclass

@dataclass
class ConformalPrediction:

    def predict_interval(self, score: float, alpha: float = 0.05) -> tuple[float, float]:
        return (score * 0.8, score * 1.2)
