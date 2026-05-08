"""Alert Router — v0.3.0 R13

Blindspot: All alerts go to single channel; no routing based on severity/type.
Risk: R13 — Critical alert buried in low-priority notifications.
"""
from dataclasses import dataclass

@dataclass
class AlertRouter:

    def route(self, severity: int) -> str:
        if severity >= 8:
            return "PAGERDUTY"
        if severity >= 5:
            return "SLACK"
        return "EMAIL"
