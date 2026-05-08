"""OTel Adapter — v0.12.0 R170

Blindspot: FLE internal telemetry incompatible with external OTel ecosystem.
Risk: R170 — FLE metrics invisible to organization-wide observability.
"""
from dataclasses import dataclass

@dataclass
class OTelAdapter:
    endpoint: str = "http://localhost:4317"
