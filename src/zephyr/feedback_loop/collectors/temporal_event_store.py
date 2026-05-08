"""Temporal Event Store — v0.3.0 R9

Blindspot: Event timeline fragmented across subsystems.
Risk: R9 — Causal ordering lost; diagnosis uses wrong temporal context.
"""
from dataclasses import dataclass, field

@dataclass
class TemporalEventStore:
    events: list[dict] = field(default_factory=list)

    def append(self, event: dict) -> None:
        self.events.append(event)
