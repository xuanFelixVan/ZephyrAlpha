"""Config Drift Detector — v0.13.0 R182

Blindspot: Configuration divergence between environment instances.
Risk: R182 — Canary config differs from production; canary validation invalid.
"""
from dataclasses import dataclass, field

@dataclass
class ConfigDrift:
    snapshots: dict[str, dict] = field(default_factory=dict)
