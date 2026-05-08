"""Chaos Engineering — v0.13.0 R172

Blindspot: No proactive failure injection to validate FLE resilience.
Risk: R172 — FLE untested under real failure conditions.
"""
from dataclasses import dataclass, field

@dataclass
class ChaosEngineering:
    experiments: list[dict] = field(default_factory=list)

    def inject(self, experiment: dict) -> None:
        self.experiments.append(experiment)
