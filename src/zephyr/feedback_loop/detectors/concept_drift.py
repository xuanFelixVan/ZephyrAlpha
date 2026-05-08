"""Concept Drift Detector — v0.5.0 R42

Blindspot: Statistical properties of metrics drift over time; static thresholds break.
Risk: R42 — EMA baseline drifts; normal behavior flagged as anomaly.
"""
from dataclasses import dataclass

@dataclass
class ConceptDrift:
    drift_detected: bool = False

    def check(self, old_distribution: list[float], new_distribution: list[float]) -> float:
        return 0.0
