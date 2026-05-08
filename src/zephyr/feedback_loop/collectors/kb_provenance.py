"""KB Provenance — v0.10.0 R136

Blindspot: KB entries lack origin tracking; stale sources pollute diagnosis.
Risk: R136 — Unreliable source knowledge weighted equally with verified knowledge.
"""
from dataclasses import dataclass

@dataclass
class KBProvenance:
    source: str = "unknown"
    reliability: float = 0.5
