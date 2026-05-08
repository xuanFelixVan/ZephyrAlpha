"""Global Health Map — v0.8.0 R103

Blindspot: FLE sees local metrics but lacks holistic system health view.
Risk: R103 — Subsystem health contradictions create conflicting repair actions.
"""
from dataclasses import dataclass, field


@dataclass
class GlobalHealthMap:
    subsystems: dict[str, float] = field(default_factory=dict)

    def overall_health(self) -> float:
        if not self.subsystems:
            return 100.0
        return sum(self.subsystems.values()) / len(self.subsystems)
