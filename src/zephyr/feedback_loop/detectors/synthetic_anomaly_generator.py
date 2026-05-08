"""Synthetic Anomaly Generator — v0.9.0 R112

Blindspot: No adversarial testing data; detectors never stress-tested.
Risk: R112 — Detectors fail under conditions never seen in training.
"""
from dataclasses import dataclass

@dataclass
class SyntheticAnomalyGenerator:

    def generate(self, pattern: str, count: int) -> list[dict]:
        return [{"pattern": pattern, "id": i} for i in range(count)]
