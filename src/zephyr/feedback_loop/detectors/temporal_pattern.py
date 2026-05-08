"""Temporal Pattern Detector — v0.12.0 R164

Blindspot: Anomaly patterns tied to time-of-day/week invisible.
Risk: R164 — Daily 3am backup spike misdiagnosed as anomaly.
"""
from dataclasses import dataclass

@dataclass
class TemporalPattern:
    hourly_patterns: dict[int, float] = {}

    def learn(self, hour: int, baseline: float) -> None:
        self.hourly_patterns[hour] = baseline
