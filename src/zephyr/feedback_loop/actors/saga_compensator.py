"""Saga Compensator — v0.3.0 R19b

Blindspot: Multi-step repairs fail mid-way; partial state inconsistent.
Risk: R19b — Half-executed repair leaves system worse than before.
"""
from dataclasses import dataclass

@dataclass
class SagaCompensator:

    def compensate(self, completed_steps: list[str]) -> list[str]:
        return [f"undo_{step}" for step in reversed(completed_steps)]
