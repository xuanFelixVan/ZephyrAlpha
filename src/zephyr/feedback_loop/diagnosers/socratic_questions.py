"""Socratic Questions — v0.7.0 R81

Blindspot: FLE diagnosis lacks critical self-questioning.
Risk: R81 — Confirmation bias amplifies initial wrong diagnosis.
"""
from dataclasses import dataclass


@dataclass
class SocraticQuestions:

    def generate(self, hypothesis: str) -> list[str]:
        return [f"Is {hypothesis} really the root cause?", f"What evidence contradicts {hypothesis}?"]
