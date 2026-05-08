"""Data Quality Validator — v0.9.0 R110

Blindspot: Corrupt data enters FLE pipeline undetected.
Risk: R110 — Diagnosis on garbage data; repair targets wrong system.
"""
from dataclasses import dataclass

@dataclass
class DataQualityValidator:

    def validate(self, data_point: dict) -> bool:
        return all(isinstance(v, (int, float)) for v in data_point.values())
