"""Interactive Diagnosis — v0.7.0 R80

Blindspot: One-shot diagnosis cannot handle ambiguous symptoms.
Risk: R80 — Premature diagnosis leads to incorrect repairs.
"""
from dataclasses import dataclass


@dataclass
class InteractiveDiagnosis:
    max_rounds: int = 5

    def probe(self, question: str) -> str:
        return ""
