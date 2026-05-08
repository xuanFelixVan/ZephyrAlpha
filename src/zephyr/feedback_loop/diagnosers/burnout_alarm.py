"""Burnout Alarm — v0.8.0 R100

Blindspot: 1-person operator burnout undetected until system failure.
Risk: R100 — Owner fatigue causes missed critical alerts and delayed responses.
"""
from dataclasses import dataclass


@dataclass
class BurnoutAlarm:
    response_latency_avg: float = 0.0
    skip_rate: float = 0.0

    @property
    def alarm(self) -> bool:
        return self.response_latency_avg > 3600.0 or self.skip_rate > 0.3
