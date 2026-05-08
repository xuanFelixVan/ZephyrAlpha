"""Schema Evolution — v0.9.0 R111

Blindspot: Metric schema changes break collectors silently.
Risk: R111 — New schema fields dropped; diagnosis misses new evidence dimensions.
"""
from dataclasses import dataclass

@dataclass
class SchemaEvolution:
    version: int = 1
