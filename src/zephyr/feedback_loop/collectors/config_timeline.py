"""Config Timeline — v0.8.0 R99

Blindspot: Config change history invisible; cannot correlate config changes with anomalies.
Risk: R99 — Post-config-change anomaly misdiagnosed as system failure.
"""
from dataclasses import dataclass, field

@dataclass
class ConfigTimeline:
    changes: list[dict] = field(default_factory=list)

    def record(self, change: dict) -> None:
        self.changes.append(change)
