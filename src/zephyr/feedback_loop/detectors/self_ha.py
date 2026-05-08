"""Self HA — v0.13.0 R173

Blindspot: Single FLE instance is SPOF for self-healing.
Risk: R173 — FLE itself fails; no other instance takes over.
"""
from dataclasses import dataclass

@dataclass
class SelfHA:
    active_instance: str = "primary"
    standby_instances: list[str] = []
