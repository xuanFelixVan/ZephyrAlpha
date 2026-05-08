"""Decision Provenance — v0.12.0 R166

Blindspot: FLE decisions lack audit trail of contributing factors.
Risk: R166 — Why was this repair chosen?  Invisible after the fact.
"""
from dataclasses import dataclass, field

@dataclass
class DecisionProvenance:
    decisions: list[dict] = field(default_factory=list)

    def record(self, decision: dict) -> None:
        self.decisions.append(decision)
