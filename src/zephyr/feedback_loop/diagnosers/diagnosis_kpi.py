"""Diagnosis KPI — v0.9.0 R116

Blindspot: No metrics on how often diagnoses lead to effective repairs.
Risk: R116 — Broken diagnosis pipeline invisible — repair feedback loop severed.
"""
from dataclasses import dataclass


@dataclass
class DiagnosisKPI:
    total: int = 0
    effective: int = 0

    @property
    def effectiveness_rate(self) -> float:
        return self.effective / max(self.total, 1)
