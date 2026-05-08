"""OpenFeature Integration — v0.13.0 R181

Blindspot: Flag evaluation not standardized; vendor lock-in.
"""
from dataclasses import dataclass

@dataclass
class OpenFeature:
    provider: str = "flagd"
