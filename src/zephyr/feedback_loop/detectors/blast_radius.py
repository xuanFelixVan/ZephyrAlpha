"""Blast Radius Detector — v0.12.0 R167

Blindspot: Repair side effects across subsystems not modeled.
Risk: R167 — Repair on subsystem A breaks subsystem B; cascading failure.
"""
from dataclasses import dataclass, field

@dataclass
class BlastRadius:
    dependency_graph: dict[str, list[str]] = field(default_factory=dict)

    def estimate(self, target: str) -> list[str]:
        return self.dependency_graph.get(target, [])
