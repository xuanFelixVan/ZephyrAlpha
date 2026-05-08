"""Digital Twin Sandbox — v0.6.0 R55

Blindspot: Repairs tested in isolation; real system complexity not replicated.
Risk: R55 — Sandbox success, production failure due to environmental differences.
"""
from dataclasses import dataclass

@dataclass
class DigitalTwinSandbox:
    fidelity: float = 0.8
