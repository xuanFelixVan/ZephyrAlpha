"""Maintenance Coordinator — v0.12.0 R168

Blindspot: Multiple maintenance windows conflict; no coordination.
Risk: R168 — Overlapping maintenance windows cause false anomaly spikes.
"""
from dataclasses import dataclass, field

@dataclass
class MaintenanceCoordinator:
    windows: list[dict] = field(default_factory=list)

    def schedule(self, window: dict) -> None:
        self.windows.append(window)
