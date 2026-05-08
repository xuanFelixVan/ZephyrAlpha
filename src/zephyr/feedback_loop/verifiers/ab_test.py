"""A/B Test Verifier — v0.9.0 R117

Blindspot: Repair effectiveness unverified via controlled experiment.
Risk: R117 — Cannot prove repair caused improvement vs. self-healing.
"""
from dataclasses import dataclass

@dataclass
class ABTest:
    control_group: float = 0.0
    treatment_group: float = 0.0

    @property
    def lift(self) -> float:
        return self.treatment_group - self.control_group
