"""Conflict Arbitration — v0.10.0 R130

Blindspot: Two subsystems propose contradictory autonomous actions.
Risk: R130 — Arbitration failure leads to oscillating repairs.
"""
from dataclasses import dataclass

@dataclass
class ConflictArbitration:

    def arbitrate(self, proposal_a: dict, proposal_b: dict) -> dict:
        return proposal_a if proposal_a.get("priority", 0) >= proposal_b.get("priority", 0) else proposal_b
