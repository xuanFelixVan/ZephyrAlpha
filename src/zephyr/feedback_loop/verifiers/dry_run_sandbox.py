"""Dry Run Sandbox — v0.3.0 R19

Blindspot: Repairs executed without sandbox validation.
Risk: R19 — Destructive repair executed on production without preview.
"""
from dataclasses import dataclass

@dataclass
class DryRunSandbox:

    def simulate(self, action: dict) -> dict:
        return {"simulated": True, "action": action}
