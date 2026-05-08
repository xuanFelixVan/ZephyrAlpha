"""LLM Quality Regression — v0.12.0 R161

Blindspot: LLM model updates cause regression in diagnostic quality.
Risk: R161 — New model version produces worse diagnoses than previous.
"""
from dataclasses import dataclass

@dataclass
class LLMQualityRegression:
    previous_accuracy: float = 0.0
    current_accuracy: float = 0.0

    @property
    def regressed(self) -> bool:
        return self.current_accuracy < self.previous_accuracy - 0.05
