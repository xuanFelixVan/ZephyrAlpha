"""Data Quality Gate — v0.11.0 R143

Blindspot: Bad data enters pipeline; FLE diagnoses data corruption as system failure.
Risk: R143 — Garbage-in causes phantom anomalies and false repairs.
"""
from dataclasses import dataclass

@dataclass
class DataQualityGate:

    def validate(self, data: dict) -> bool:
        return all(v is not None for v in data.values())
